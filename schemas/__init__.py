"""Structured output schemas for every agent, one module per agent output.

Rule: this package holds data shapes only. It must not import agents, db_store,
memory or llm code, so tools, tests and scripts can import it safely. Its only
allowed project import is agent/tools/formula_library.py (a plain-dict module).

Modules:
    requirements.py  RequirementSpec      (requirements agent)
    components.py    ComponentChoices     (component selection agent → cost estimation)
Planned:
    sizing.py        SizingTable          (capacity modeling agent)
    cost.py          CostBreakdown        (cost estimation agent)
    topology.py      TopologyGraph        (architecture composer agent)
    findings.py      Findings             (design critic agent)
"""

from schemas.components import (
    ComponentChoice,
    ComponentChoices,
    EngineName,
    ServiceName,
)
from schemas.requirements import (
    ASSUMPTION_KEYS,
    SYSTEM_TYPES,
    AssumptionKey,
    AwsRegion,
    ExplicitRequirements,
    RequirementSpec,
    SystemType,
)

__all__ = [
    "ASSUMPTION_KEYS",
    "SYSTEM_TYPES",
    "AssumptionKey",
    "AwsRegion",
    "ComponentChoice",
    "ComponentChoices",
    "EngineName",
    "ExplicitRequirements",
    "RequirementSpec",
    "ServiceName",
    "SystemType",
]
