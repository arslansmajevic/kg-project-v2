# 2 - construction

Code and data used to **create** the knowledge graph (report Section 2, LO7).

## Contents to include
- `generate_data.py` — generates the observed-style log triples.
- `rules.py` — derives `suggests_technique` / `has_provenance` facts (also used in `4 - logic`).
- `data/` — the self-constructed dataset:
  - `base_triples.tsv` — observed synthetic log-like facts.
  - `derived_rule_triples.tsv` — rule-created facts with provenance.
  - `all_triples.tsv` — the union used for the KGE experiment.
- `requirements.txt`, `run_project.sh` — environment and one-shot pipeline.

## How to run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate_data.py        # writes the TSV triple files into data/
```
The dataset is self-constructed and included in full here, so results are fully
reproducible without any external download.
