# Submission layout (single PDF + single ZIP)

This folder defines how the **ZIP file** accompanying the portfolio PDF should be
organised, following the Knowledge Graphs course "Portfolio Example Structure".

## The two deliverables

1. **One PDF** — the compiled report in `overleaf/main.tex`.
   - The PDF filename **must end in `-structured.pdf`** because this submission
     uses the example structure (e.g. `knowledge-graphs-portfolio-structured.pdf`).
   - It already contains the briefer learning-outcome cover pages and the five
     sections (1 Scenario, 2 KG Construction, 3 ML-based Representation,
     4 Logic-based Representation, 5 Reflection) so each LO can be located quickly.

2. **One ZIP** — built from the subfolders here, one per report part:
   - `2 - construction` — code and data to build the KG (report Section 2).
   - `3 - ML` — KGE training, evaluation and results (report Section 3).
   - `4 - logic` — the symbolic rule layer (report Section 4).
   - `5 - reflection` — supporting artefacts referenced in the reflection (Section 5).

Each subfolder contains a `readme.md` explaining what it holds and how to run it.

## How to assemble the ZIP

The runnable code lives at the repository root (`src/`, `data/`,
`experiments/`). Each subfolder's `readme.md` lists exactly which repository
files to copy into it. From the repository root you can populate the folders
with:

```bash
# Section 2 - construction
cp src/generate_data.py src/rules.py requirements.txt run_project.sh "submission/2 - construction/"
cp -r data "submission/2 - construction/"

# Section 3 - ML
cp src/train.py requirements.txt "submission/3 - ML/"
cp -r experiments "submission/3 - ML/"

# Section 4 - logic
cp src/rules.py "submission/4 - logic/"

# Section 5 - reflection
cp DATA_CARD.md RUN_PLAN.md REPORT_GUIDE.md "submission/5 - reflection/"
```

Then zip the `submission/` folder. The `data/` directory is the
self-constructed dataset and is small enough to include in full, giving full
reproducibility.
