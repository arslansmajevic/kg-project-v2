# Data card — Synthetic APT-style security knowledge graph

## Purpose and status

This is a **synthetic teaching dataset**, generated locally by
`src/generate_data.py`. It is not LANL telemetry, it contains no real people,
hosts or incidents, and it does not provide ground-truth APT labels. Its role is
to provide a compact, reproducible graph for testing a PyKEEN pipeline on a
laptop.

The graph is semantically inspired by enterprise security telemetry and four
MITRE ATT&CK technique identifiers. The use of ATT&CK names makes the schema
interpretable; it does not validate the generated events as attacks.

## Exact contents after generation

| Item | Count | How it is generated |
|---|---:|---|
| Total triples | 1,232 | 944 observed-style + 288 rule-derived |
| Entities | 245 | Pseudonymous users, hosts, processes, file kinds, process families, roles, techniques and provenance |
| Relations | 9 | Seven observed-style relations and two derived relations |
| Processes | 180 | `process_000` to `process_179` |
| Users | 18 | `user_00` to `user_17` |
| Workstations | 12 | `workstation_00` to `workstation_11` |
| Servers | 8 | `server_00` to `server_07` |
| Process families | 5 | PowerShell, remote desktop, downloader, credential dump, benign office |
| File entities | 15 | Three synthetic file kinds per family |
| ATT&CK-like technique nodes | 4 | T1059, T1021, T1105 and T1003 labels |

The number of triples is deterministic. Re-running `python src/generate_data.py`
recreates the same graph.

## Observed-style facts: 944 triples

These triples simulate what could be assembled from endpoint, identity, network
and asset-inventory systems. They are **not observed real logs**.

| Relation | Count | Interpretation |
|---|---:|---|
| `authenticates_to` | 36 | User authenticated to workstation |
| `runs` | 180 | Workstation ran process |
| `executed_by` | 180 | Process executed by user |
| `has_family` | 180 | Process assigned a synthetic family |
| `accesses` | 180 | Process accessed a synthetic file kind |
| `connects_to` | 180 | Process connected to a server or workstation |
| `has_role` | 8 | Server is high-value or standard |

## Rule-derived facts: 288 triples

The rule layer applies the following deterministic rule:

```text
has_family(Process, Family) AND family_maps_to_technique(Family, Technique)
    -> suggests_technique(Process, Technique)
```

For the four attack-oriented families, the rule adds two triples for every
process: one `suggests_technique` triple and one `has_provenance` triple. There
are 36 processes in each family, so 4 × 36 × 2 = 288 derived triples. The
benign-office family is intentionally unmapped and generates no technique
suggestion.

| Synthetic family | Technique label in graph | Interpretation |
|---|---|---|
| `family_powershell` | `attack_T1059_command_and_scripting` | Command/scripting activity; a simplified parent-technique mapping |
| `family_remote_desktop` | `attack_T1021_remote_services` | Remote-service activity; a simplified parent-technique mapping |
| `family_downloader` | `attack_T1105_ingress_tool_transfer` | Transfer of a tool/file into an environment |
| `family_credential_dump` | `attack_T1003_os_credential_dumping` | Credential material obtained from operating-system sources |

## What the labels mean

`suggests_technique` is a **rule-generated hypothesis label**, not a confirmed
malicious event and not an independent ground-truth label. Therefore, a KGE
result evaluates recovery of held-out graph links, not detection accuracy,
precision/recall, or business risk.

The generator deliberately produces a regular pattern: family, file kind and
network behaviour are correlated. This makes the dataset suitable for a small
feasibility experiment but easier than real SOC telemetry. Report this as a
limitation, rather than interpreting a high score as attack-detection ability.

## Relation to the intended real-data project

The project proposal names LANL security data and MITRE ATT&CK as the planned
real-data direction. This dataset is phase 1: an implementation of the
architecture and evaluation workflow before a carefully documented,
time-bounded real-data subset is introduced.

A real extension should:

1. document original source fields and their transformations;
2. keep pseudonymous but stable identifiers;
3. preserve timestamps and use a chronological split;
4. obtain independent incident/technique labels where possible; and
5. keep rule-derived facts separate from observed facts and their provenance.
