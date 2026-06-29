"""Train and evaluate small KGE models for the synthetic APT-style security KG.

The script supports a clean validation-then-test workflow:

1. Run candidate configurations with ``--evaluation-split validation``.
2. Choose one configuration using only validation results.
3. Run that configuration once with ``--evaluation-split test``.

This is a feasibility experiment, not an operational intrusion-detection system.
Its research question is:

  Can a KGE rank plausible missing process -> technique links in a compact,
  hybrid (observed facts + rule-derived facts) enterprise security KG?
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pykeen.evaluation import RankBasedEvaluator
from pykeen.pipeline import pipeline
from pykeen.predict import predict_target
from pykeen.triples import TriplesFactory

from generate_data import main as generate_data

logging.getLogger("pykeen").setLevel(logging.WARNING)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "all_triples.tsv"
DEFAULT_RESULTS_DIR = ROOT / "results"
TARGET_RELATION = "suggests_technique"


def load_labeled_triples(path: Path) -> np.ndarray:
    """Load three-column TSV triples without treating the first row as a header."""
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            if len(row) != 3:
                raise ValueError(f"Expected 3 columns, found {len(row)} in row {row!r}")
            rows.append(row)
    return np.asarray(rows, dtype=str)


def metric(result, name: str) -> float:
    """Fetch a stable, paper-friendly rank-based metric from PyKEEN."""
    metric_results = getattr(result, "metric_results", result)
    return float(metric_results.get_metric(name))


def metrics_from_result(result, prefix: str) -> dict[str, float]:
    """Return the global, filtered link-prediction metrics used in the report."""
    return {
        f"{prefix}_filtered_MRR": metric(result, "both.realistic.inverse_harmonic_mean_rank"),
        f"{prefix}_filtered_Hits@1": metric(result, "both.realistic.hits_at_1"),
        f"{prefix}_filtered_Hits@3": metric(result, "both.realistic.hits_at_3"),
        f"{prefix}_filtered_Hits@10": metric(result, "both.realistic.hits_at_10"),
        f"{prefix}_filtered_mean_rank": metric(result, "both.realistic.arithmetic_mean_rank"),
    }


def evaluate_technique_tail_prediction(
    *,
    model,
    evaluation: TriplesFactory,
    known_positive_factories: list[TriplesFactory],
) -> dict[str, float | int]:
    """Evaluate the analyst-facing task: process + relation -> ATT&CK-like technique.

    This is deliberately reported separately from global link prediction.
    The candidate set is restricted to the four ``attack_*`` technique nodes and
    only the missing tail is ranked. It must never be compared numerically with
    global MRR because the task and candidate set are different.
    """
    relation_id = evaluation.relation_to_id.get(TARGET_RELATION)
    if relation_id is None:
        return {
            "technique_tail_test_triples": 0,
            "technique_tail_type_constrained_MRR": float("nan"),
            "technique_tail_type_constrained_Hits@1": float("nan"),
            "technique_tail_type_constrained_Hits@3": float("nan"),
        }

    target_mask = evaluation.mapped_triples[:, 1] == relation_id
    target_triples = evaluation.mapped_triples[target_mask]
    technique_ids = [
        entity_id
        for entity_label, entity_id in evaluation.entity_to_id.items()
        if entity_label.startswith("attack_")
    ]
    if target_triples.shape[0] == 0 or not technique_ids:
        return {
            "technique_tail_test_triples": int(target_triples.shape[0]),
            "technique_tail_type_constrained_MRR": float("nan"),
            "technique_tail_type_constrained_Hits@1": float("nan"),
            "technique_tail_type_constrained_Hits@3": float("nan"),
        }

    evaluator = RankBasedEvaluator(filtered=True)
    result = evaluator.evaluate(
        model=model,
        mapped_triples=target_triples,
        additional_filter_triples=tuple(factory.mapped_triples for factory in known_positive_factories),
        restrict_entities_to=technique_ids,
        pre_filtered_triples=True,
        do_time_consuming_checks=False,
        targets=("tail",),
        batch_size=256,
        use_tqdm=False,
    )
    return {
        "technique_tail_test_triples": int(target_triples.shape[0]),
        "technique_tail_type_constrained_MRR": metric(result, "tail.realistic.inverse_harmonic_mean_rank"),
        "technique_tail_type_constrained_Hits@1": metric(result, "tail.realistic.hits_at_1"),
        "technique_tail_type_constrained_Hits@3": metric(result, "tail.realistic.hits_at_3"),
    }


def train_one_model(
    *,
    model_name: str,
    training: TriplesFactory,
    validation: TriplesFactory,
    evaluation: TriplesFactory,
    output_dir: Path,
    epochs: int,
    embedding_dim: int,
    model_seed: int,
    learning_rate: float,
    batch_size: int,
    evaluation_split: str,
) -> dict[str, float | int | str]:
    """Run one reproducible KGE experiment and save its artifacts."""
    result = pipeline(
        training=training,
        validation=validation,
        testing=evaluation,
        model=model_name,
        model_kwargs={"embedding_dim": embedding_dim},
        optimizer="Adam",
        optimizer_kwargs={"lr": learning_rate},
        training_kwargs={"num_epochs": epochs, "batch_size": batch_size},
        evaluator="RankBasedEvaluator",
        evaluator_kwargs={"filtered": True},
        random_seed=model_seed,
        device="cpu",  # Laptop-friendly and reproducible on Intel and Apple Silicon Macs.
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    result.save_to_directory(output_dir)

    # Save a transparent loss plot for a report figure.
    plt.figure()
    plt.plot(result.losses)
    plt.xlabel("Epoch")
    plt.ylabel("Training loss")
    plt.title(f"{model_name} training loss")
    plt.tight_layout()
    plt.savefig(output_dir / "loss_curve.png", dpi=180)
    plt.close()

    # The process is known to be in the graph, while the target technique is
    # left for the model to rank. This is an example investigation query.
    predictions = predict_target(
        model=result.model,
        head="process_000",
        relation=TARGET_RELATION,
        triples_factory=training,
    )
    predictions.df.head(10).to_csv(output_dir / "example_link_predictions.csv", index=False)

    # During a validation trial, only training facts are known positives. During
    # final testing, validation facts are known positives too.
    known_for_filtering = [training]
    if evaluation_split == "test":
        known_for_filtering.append(validation)

    row: dict[str, float | int | str] = {
        "model": model_name,
        "evaluation_split": evaluation_split,
        "epochs": epochs,
        "embedding_dim": embedding_dim,
        "model_seed": model_seed,
        "learning_rate": learning_rate,
        "batch_size": batch_size,
    }
    row.update(metrics_from_result(result, prefix="evaluation"))
    row.update(
        evaluate_technique_tail_prediction(
            model=result.model,
            evaluation=evaluation,
            known_positive_factories=known_for_filtering,
        )
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=80, help="Epochs per model (default: 80).")
    parser.add_argument("--embedding-dim", type=int, default=32, help="Embedding dimension (default: 32).")
    parser.add_argument("--learning-rate", type=float, default=0.01, help="Adam learning rate (default: 0.01).")
    parser.add_argument("--batch-size", type=int, default=256, help="Training batch size (default: 256).")
    parser.add_argument("--split-seed", type=int, default=42, help="Seed for the train/validation/test split.")
    parser.add_argument("--model-seed", type=int, default=42, help="Seed for model initialisation/training.")
    parser.add_argument(
        "--evaluation-split",
        choices=["validation", "test"],
        default="test",
        help="Use validation while selecting configurations; use test once for the final configuration.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["TransE", "ComplEx"],
        choices=["TransE", "ComplEx"],
        help="One or both models to run.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory for this run's artifacts (default: results/).",
    )
    parser.add_argument("--keep-results", action="store_true", help="Do not delete the selected output directory first.")
    args = parser.parse_args()

    generate_data()
    results_dir = args.output_dir.resolve()
    if results_dir.exists() and not args.keep_results:
        shutil.rmtree(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    labeled_triples = load_labeled_triples(DATA_PATH)
    factory = TriplesFactory.from_labeled_triples(labeled_triples)
    training, validation, testing = factory.split([0.80, 0.10, 0.10], random_state=args.split_seed)
    evaluation = validation if args.evaluation_split == "validation" else testing

    split_summary = {
        "total_triples": int(factory.num_triples),
        "entities": int(factory.num_entities),
        "relations": int(factory.num_relations),
        "training_triples": int(training.num_triples),
        "validation_triples": int(validation.num_triples),
        "testing_triples": int(testing.num_triples),
        "split_seed": args.split_seed,
        "model_seed": args.model_seed,
        "models": args.models,
        "epochs": args.epochs,
        "embedding_dim": args.embedding_dim,
        "learning_rate": args.learning_rate,
        "batch_size": args.batch_size,
        "evaluation_split": args.evaluation_split,
    }
    (results_dir / "experiment_configuration.json").write_text(
        json.dumps(split_summary, indent=2), encoding="utf-8"
    )

    print("\nKnowledge graph summary")
    for key, value in split_summary.items():
        print(f"  {key}: {value}")

    rows = []
    for model_name in args.models:
        print(f"\nTraining {model_name} ...")
        rows.append(
            train_one_model(
                model_name=model_name,
                training=training,
                validation=validation,
                evaluation=evaluation,
                output_dir=results_dir / model_name.lower(),
                epochs=args.epochs,
                embedding_dim=args.embedding_dim,
                model_seed=args.model_seed,
                learning_rate=args.learning_rate,
                batch_size=args.batch_size,
                evaluation_split=args.evaluation_split,
            )
        )

    metrics = pd.DataFrame(rows).sort_values("evaluation_filtered_MRR", ascending=False)
    metrics.to_csv(results_dir / "metrics_comparison.csv", index=False)
    print("\nFinal filtered link-prediction results")
    print(metrics.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print(f"\nSaved report-ready files under: {results_dir}")


if __name__ == "__main__":
    main()
