"""ORCHESTRA: Baselines Package.

Provides pluggable multi-agent baseline topologies, runners, and comparative evaluation
for rigorous empirical benchmark comparisons against ORCHESTRA.
"""

from baselines.topologies import (
    SUPPORTED_BASELINES,
    BaseTopologyEnforcer,
    BroadcastTopology,
    CentralCoordinatorTopology,
    FixedRolesTopology,
    HierarchicalCoordinatorTopology,
    IndependentTopology,
    OrchestraTopology,
    create_baseline_topology,
)

__all__ = [
    "BaseTopologyEnforcer",
    "IndependentTopology",
    "BroadcastTopology",
    "CentralCoordinatorTopology",
    "HierarchicalCoordinatorTopology",
    "FixedRolesTopology",
    "OrchestraTopology",
    "SUPPORTED_BASELINES",
    "create_baseline_topology",
]
