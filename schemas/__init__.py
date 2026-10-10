"""Structured output schemas for every agent, one module per agent output.

Rule: this package holds data shapes only. It must not import agents, db_store,
memory or llm code, so tools, tests and scripts can import it safely. Its only
allowed project import is agent/tools/formula_library.py (a plain-dict module).

Modules:
    requirements.py  RequirementSpec      (requirements agent)
Planned:
    sizing.py        SizingTable          (capacity modeling agent)
    components.py    ComponentChoices     (component selection agent)
    cost.py          CostBreakdown        (cost estimation agent)
    topology.py      TopologyGraph        (architecture composer agent)
    findings.py      Findings             (design critic agent)
"""

from schemas.requirements import (
    ASSUMPTION_KEYS,
    SYSTEM_TYPES,
    AssumptionKey,
    ExplicitRequirements,
    RequirementSpec,
    SystemType,
)

__all__ = [
    "ASSUMPTION_KEYS",
    "SYSTEM_TYPES",
    "AssumptionKey",
    "ExplicitRequirements",
    "RequirementSpec",
    "SystemType",
]
