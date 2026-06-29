# 4 - logic

The **logic-based representation**: the symbolic rule layer (report Section 4,
LO2/LO6/LO8).

## Contents to include
- `rules.py` — a dependency-free, inspectable Datalog-style rule:
  ```
  has_family(Process, Family) AND family_maps_to_technique(Family, Technique)
      -> suggests_technique(Process, Technique)
  ```
  Each derived suggestion also creates a `has_provenance` fact so the symbolic
  origin of every derived edge is recorded in the graph.

## How to run
`rules.py` is imported by the construction pipeline (`generate_data.py`). To
apply the rules directly to a list of base triples, call `apply_rules(...)` from
Python. The four `family -> technique` mappings are defined in
`FAMILY_TO_TECHNIQUE` at the top of the file and can be extended there.
