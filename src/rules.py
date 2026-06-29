"""Tiny transparent rule layer for the synthetic security knowledge graph.

This file deliberately does not depend on a Datalog engine. It makes the
logical part of the project inspectable and easy to replace later with Vadalog
or another reasoner.

Rule in Datalog-like notation:

  has_family(Process, Family) AND family_maps_to_technique(Family, Technique)
      -> suggests_technique(Process, Technique)

The resulting triples are provenance-labelled so that the report can explain
that they were created by symbolic rules, not observed directly in logs.
"""

from __future__ import annotations

from collections.abc import Iterable

Triple = tuple[str, str, str]

FAMILY_TO_TECHNIQUE = {
    "family_powershell": "attack_T1059_command_and_scripting",
    "family_remote_desktop": "attack_T1021_remote_services",
    "family_downloader": "attack_T1105_ingress_tool_transfer",
    "family_credential_dump": "attack_T1003_os_credential_dumping",
}


def apply_rules(base_triples: Iterable[Triple]) -> list[Triple]:
    """Derive technique hypotheses from process-family evidence.

    Only a process's explicit ``has_family`` fact is used here. This is a
    simplification for a coursework prototype: rules are deterministic,
    auditable, and intentionally separate from the KGE model.
    """
    derived: set[Triple] = set()

    for head, relation, tail in base_triples:
        if relation != "has_family":
            continue
        technique = FAMILY_TO_TECHNIQUE.get(tail)
        if technique is not None:
            derived.add((head, "suggests_technique", technique))
            derived.add((head, "has_provenance", "rule_family_to_attack_technique"))

    return sorted(derived)
