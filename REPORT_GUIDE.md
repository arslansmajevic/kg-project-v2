# Report guide — PyKEEN security KG feasibility experiment

## Suggested title

**Hybrid Knowledge Graph Embeddings for Ranking Security-Event Technique Links: A Small PyKEEN Feasibility Study**

## Research question

Can a compact hybrid knowledge graph, consisting of observed security-event
facts and rule-derived technique hypotheses, support link prediction of missing
`process -> suggests_technique -> ATT&CK-like technique` triples?

## Method paragraph (adapt only after you run the code)

We modelled a synthetic enterprise-security knowledge graph as labelled triples.
The graph contains users, workstations, servers, processes, files, process
families, security roles and ATT&CK-like techniques. Observed facts include
`authenticates_to`, `runs`, `executed_by`, `has_family`, `accesses`,
`connects_to`, and `has_role`. A deterministic Datalog-style rule derives
`suggests_technique` triples from process-family evidence and adds a provenance
fact. We randomly split triples 80/10/10 into training, validation and testing
sets using seed 42. We trained TransE and ComplEx with a 32-dimensional
embedding, Adam optimisation (learning rate 0.01) and [INSERT EPOCHS] epochs.
We assessed filtered link prediction using MRR, Hits@1, Hits@3, Hits@10 and mean
rank.

## Results table template

Replace every bracketed field with the values in `results/metrics_comparison.csv`.

| Model | Filtered MRR | Hits@1 | Hits@3 | Hits@10 | Mean Rank |
|---|---:|---:|---:|---:|---:|
| TransE | [ ] | [ ] | [ ] | [ ] | [ ] |
| ComplEx | [ ] | [ ] | [ ] | [ ] | [ ] |

## Interpretation prompts

* Which model had higher filtered MRR? State the observed number, not a broad
  claim about KGE models in general.
* Is the best model better at placing held-out true links near the top of the
  candidate list? Refer to Hits@k.
* Does the loss curve stabilise? Describe it without treating a low training
  loss as proof of generalisation.
* Show the top-ranked candidate techniques for `process_000`. Call them ranked
  hypotheses, not detections or probabilities.

## Learning-outcome discussion points

**LO1:** TransE represents relations as translations in embedding space;
ComplEx uses complex-valued embeddings and can represent more varied relational
patterns. The experiment compares them through the same held-out link
prediction task.

**LO2:** The rule is explicit, inspectable and separate from training. This
shows why a symbolic layer can produce provenance-aware facts. The code does
not implement full recursive or existential Datalog reasoning; say this
clearly.

**LO4:** The generator naturally resembles a property graph because log events
are typed entities with labelled edges. PyKEEN consumes three-column labelled
triples, which resembles an RDF-style statement view. This is a modelling
choice, not proof that either model is universally better.

**LO5:** The architecture is modular: ingestion/generation -> rule engine ->
triple store -> KGE training/evaluation -> ranked analyst output. In a real
system, raw telemetry would live outside the embedding model and only selected,
versioned KG facts would be embedded.

**LO6 and LO8:** The KGE serves as approximate KG completion by ranking missing
links. The rule engine serves as deterministic reasoning. These are different
forms of inference and should not be conflated.

**LO9 and LO11:** A SOC analyst could review a ranked list of candidate
technique links alongside the rule provenance and raw evidence. Human review is
necessary because KGE scores are not calibrated security risk values.

**LO12:** The project demonstrates a hybrid design: logic creates transparent
facts, while ML generalises patterns in the graph. Neither component alone
makes the system a complete AI-based security product.

## Limitations to include

1. The data are synthetic and intentionally regular, so results cannot be
   generalised to real APT detection.
2. The random triple split is appropriate for a teaching KGE benchmark but can
   leak temporal information in a log setting. A real extension needs a
   chronological split.
3. Ranking metrics test the ability to recover withheld triples, not alert
   precision/recall on independently labelled incidents.
4. The rules are intentionally simple and do not cover MITRE ATT&CK in full.
5. Hyperparameters are small and illustrative; no comprehensive HPO was run.

## Safe next extension

Replace `generate_base_triples()` with a converter for a small, documented
window of one data source. Keep stable pseudonymous identifiers, add timestamp
handling separately, create a chronological split, and retain the exact rule
set and configuration used for each run.
