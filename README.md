# Lightweight Knowledge Graph Embedding project: APT-style security events

A small, reproducible PyKEEN feasibility experiment designed as a recovery path
from an oversized LANL prototype. It trains **TransE** and **ComplEx** on a
synthetic enterprise-security knowledge graph, evaluates filtered link
prediction, and writes report-ready CSV and PNG files.

> **Academic scope.** This is a feasibility prototype, not an APT detector. Its
> synthetic data are deliberately small and interpretable. Do not claim that its
> metrics measure real-world attack detection.

## What is new in this version

The script now separates **validation** selection from final **test** reporting
and lets each experiment write to its own directory. Start with
[`RUN_PLAN.md`](RUN_PLAN.md), then use [`DATA_CARD.md`](DATA_CARD.md) as the
precise description of the dataset in your report.

## Architecture

```text
synthetic event facts --> transparent rules --> hybrid KG --> PyKEEN KGE
     (observed-style)      (derived facts)      (triples)     (ranking/evaluation)
```

- `src/generate_data.py` creates observed-style log triples.
- `src/rules.py` implements a small Datalog-style family-to-technique rule and
  records provenance.
- `src/train.py` splits the KG into train/validation/test sets, trains TransE
  and/or ComplEx, and reports global plus analyst-oriented metrics.

## Quick start on macOS

Use Python 3.10, 3.11 or 3.12. From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python src/train.py \
  --models TransE ComplEx \
  --epochs 80 --embedding-dim 32 \
  --evaluation-split validation \
  --output-dir experiments/first_validation_run
```

For the full experiment sequence, follow `RUN_PLAN.md`.

## Reading the results

- `evaluation_filtered_MRR`, Hits@k and mean rank: global filtered
  link-prediction metrics. Higher MRR/Hits@k and lower mean rank are better.
- `technique_tail_type_constrained_*`: a different, analyst-facing task. It
  ranks only the candidate ATT&CK-like technique tail for
  `(process, suggests_technique, ?)`. Do **not** compare it numerically with
  global MRR because its candidate set is restricted to technique nodes.
- `loss_curve.png`: training optimisation evidence, not by itself a measure of
  generalisation.

Filtered evaluation avoids penalising a model for ranking another known true
triple above the evaluated one.

## Evidence for the learning outcomes

| Learning outcome | Concrete evidence in this project |
|---|---|
| LO1 | Train and compare TransE and ComplEx on the same KG task. |
| LO2 | `rules.py` implements an explicit inspectable rule and provenance facts. |
| LO4 | Observed-style telemetry is represented as labelled triples; the data card explains the property-graph-to-triple view. |
| LO5 | Ingestion/generation → rule engine → triple store → KGE → ranked output is modular. |
| LO6 | Filtered link prediction shows approximate KG completion; rules show deterministic inference. |
| LO7 | `generate_data.py` is a reproducible KG-creation pipeline. |
| LO8 | Held-out links form the KG-completion task. |
| LO9 | The analyst-oriented query mirrors a SOC hypothesis-ranking workflow. |
| LO11 | `example_link_predictions.csv` is a small analyst-facing service output. |
| LO12 | The rule layer is symbolic; PyKEEN supplies the ML embedding layer. |

LO3 and LO10 are intentionally outside scope.

## Limitations that must appear in the report

1. The data are synthetic and deliberately regular; results do not generalise
   to operational APT detection.
2. `suggests_technique` links are rule-derived labels, not independent attack
   ground truth.
3. The random split is a KGE teaching split, not a time-safe log evaluation.
   A real log experiment should use chronological separation.
4. Global KGE rankings are not alert precision/recall or calibrated risk scores.
5. This prototype implements a simple deterministic rule, not full recursive
   or existential Datalog reasoning.
