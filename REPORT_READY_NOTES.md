# Report-ready notes (adapt to your actual final results)

## How to describe the original 1,000-epoch ComplEx result

The 1,000-epoch ComplEx exploratory run obtained filtered MRR 0.114, Hits@1
0.040, Hits@3 0.105, Hits@10 0.246 and mean rank 52.65. It should not be used
as a definitive comparison with the earlier TransE result unless both models
were trained with the same split, epoch count, embedding dimension, optimiser,
learning rate and random seed. The result does show that simply increasing the
epoch count did not automatically yield a stronger score in this configuration.
It is consistent with, but does not prove, a training-budget/optimisation issue;
validation results and loss curves are needed for a justified conclusion.

## Data statement

We constructed a deterministic synthetic enterprise-security knowledge graph
with 1,232 labelled triples, 245 entities and 9 relations. The observed-style
component contains 944 triples representing pseudonymous users, workstations,
servers, processes, file kinds and asset roles. A transparent rule layer derives
288 additional facts. For four synthetic process families, the rule maps a
`has_family` observation to an ATT&CK-inspired `suggests_technique` hypothesis
and stores a provenance relation. The graph labels are semantically grounded in
MITRE ATT&CK technique identifiers, but the events and labels are generated
locally rather than collected from real incidents.

## Interpretation statement

The global filtered MRR measures the model's ability to rank withheld true
triples among candidate entity replacements across the whole graph. It is not
alert precision, attack recall or a calibrated likelihood of compromise. The
application-aligned technique-tail metric is reported separately because it
answers a narrower query—given a process and `suggests_technique`, which of the
four technique nodes should be ranked highest?

## Limitation statement

The target technique links are derived from a deterministic family-to-technique
rule. Consequently, the experiment evaluates whether a KGE can recover a
structured, rule-generated pattern from the rest of the graph; it does not show
that the model detects independently labelled APT activity. In a real extension,
technique labels should be independently sourced or time-bounded, and the data
split should follow time order to prevent future information from influencing
training.
