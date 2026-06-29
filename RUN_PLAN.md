# Experimental plan — valid, small, reportable iterations

## Rule zero: do not select a model using test results

Use `--evaluation-split validation` to choose a configuration. Only after you
have fixed a model, epoch count and embedding dimension should you run the same
configuration with `--evaluation-split test`.

The existing earlier runs are useful **exploratory baselines**. Do not present a
comparison between TransE at one epoch count and ComplEx at a different epoch
count as a fair model comparison.

All commands assume the virtual environment is active and you are in the
project folder.

## A. Fair model comparison

Both models get exactly the same split, embedding dimension, epochs, learning
rate and batch size. Select the better model using validation MRR.

```bash
python src/train.py \
  --models TransE ComplEx \
  --epochs 80 --embedding-dim 32 \
  --split-seed 42 --model-seed 42 \
  --evaluation-split validation \
  --output-dir experiments/A_models_e80_d32
```

**Report question:** Under an identical training budget, which model has the
higher validation MRR and Hits@10? Do not claim that one architecture is
universally better; only describe this graph and configuration.

## B. Training-duration sensitivity

Pick the model with the best validation MRR in A. Replace `TransE` below if
ComplEx won. Hold every other setting fixed. These are validation runs.

```bash
for e in 20 80 200; do
  python src/train.py \
    --models TransE \
    --epochs "$e" --embedding-dim 32 \
    --split-seed 42 --model-seed 42 \
    --evaluation-split validation \
    --output-dir "experiments/B_transe_e${e}_d32"
done
```

**Report question:** Does validation MRR improve, plateau or decline as the
training budget grows? The loss curve measures optimisation; it is not evidence
of generalisation by itself.

## C. Embedding-capacity sensitivity

Using the selected model and selected epoch count, vary the dimension only.
For example, keep 80 epochs if B does not justify changing it.

```bash
for d in 16 32 64; do
  python src/train.py \
    --models TransE \
    --epochs 80 --embedding-dim "$d" \
    --split-seed 42 --model-seed 42 \
    --evaluation-split validation \
    --output-dir "experiments/C_transe_e80_d${d}"
done
```

**Report question:** Does more representational capacity help on this small,
regular graph? A higher dimension has more parameters; a worse validation score
is plausible and informative.

## D. One final test evaluation

Choose one configuration from A–C **using validation metrics only**. Example
below assumes TransE, 80 epochs and dimension 32 were chosen.

```bash
python src/train.py \
  --models TransE \
  --epochs 80 --embedding-dim 32 \
  --split-seed 42 --model-seed 42 \
  --evaluation-split test \
  --output-dir experiments/D_final_test
```

Use only this row as the headline test result in the report.

## E. Optional robustness across model seeds

This is a small stability check after the configuration has been fixed. The
split is kept fixed, so the only planned source of variation is stochastic model
initialisation/training.

```bash
for s in 7 42 1337; do
  python src/train.py \
    --models TransE \
    --epochs 80 --embedding-dim 32 \
    --split-seed 42 --model-seed "$s" \
    --evaluation-split test \
    --output-dir "experiments/E_seed_${s}"
done
```

Report the three test MRR values, their mean and standard deviation. Do not pick
the best seed as the result.

## Separate, application-aligned metric

Each run also reports `technique_tail_type_constrained_*`. This ranks only the
tail of `(process, suggests_technique, ?)` among the four ATT&CK-like technique
nodes. It is useful for describing the analyst-facing question, but it has a
smaller candidate set than global link prediction. Never compare this number
directly with global MRR.

## What not to do

- Do not compare different epoch counts and call it a model comparison.
- Do not report only the best among many test runs.
- Do not claim a rule-only result is an independent detection baseline: the
  target labels were created by that rule.
- Do not compare `base_triples.tsv` versus `all_triples.tsv` as though their
  MRR values measured the same task; the graphs and relations differ.
- Do not call a KGE score a probability of compromise or a confirmed alert.
