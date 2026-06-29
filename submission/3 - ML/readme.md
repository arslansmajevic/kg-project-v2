# 3 - ML

The **ML-based representation**: Knowledge Graph Embedding training and
evaluation (report Section 3, LO1/LO6/LO8).

## Contents to include
- `train.py` — splits the KG 80/10/10, trains TransE and ComplEx with PyKEEN,
  and writes metrics, ranked predictions and loss curves.
- `experiments/` — the runs reported in Section 3:
  - `A_models_e80_d32` — fair TransE vs ComplEx comparison (Run A).
  - `B_transe_e{20,80,200}_d32` — training-duration sensitivity (Run B).
  - `C_transe_e80_d{16,32,64}` — embedding-dimension sensitivity (Run C).
  - `D_final_test` — final held-out test (Run D).
  - `E_seed_{7,42,1337}` — seed-robustness check (Run E).
- `requirements.txt` — Python dependencies.

## How to run (example: Run A)
```bash
python train.py \
  --models TransE ComplEx \
  --epochs 80 --embedding-dim 32 \
  --evaluation-split validation \
  --output-dir experiments/A_models_e80_d32
```
Each run directory contains `metrics_comparison.csv`, per-model `results.json`,
`example_link_predictions.csv` and `loss_curve.png`.
