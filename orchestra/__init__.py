"""ORCHESTRA: Research Framework for Emergent Organizational Evolution in Multi-Agent Systems.

Targets empirical investigation of organizational emergence, specialization,
communication topology evolution, resilience under perturbations, and human oversight.
"""

__version__ = "0.1.0"

_EXPORTS = {
    # Configuration
    "ExperimentConfig": "orchestra.config",
    "SUPPORTED_AGENT_SCALES": "orchestra.config",
    "SUPPORTED_PROTOCOLS": "orchestra.config",
    # Runner & Batch Matrix
    "run_orchestra_experiment": "orchestra.runner",
    "ExperimentSummary": "orchestra.runner",
    "MatrixConfig": "orchestra.batch_runner",
    "run_batch_matrix": "orchestra.batch_runner",
    # Instrumentation & Metrics
    "OrganizationalProfile": "orchestra.instrumentation",
    "RoundNetworkSnapshot": "orchestra.instrumentation",
    "calculate_gini": "orchestra.instrumentation",
    "calculate_entropy": "orchestra.instrumentation",
    "extract_round_snapshot": "orchestra.instrumentation",
    "extract_case_instrumentation": "orchestra.instrumentation",
    "save_orchestra_instrumentation": "orchestra.instrumentation",
    # Perturbations
    "BasePerturbation": "orchestra.perturbations",
    "AgentDropoutPerturbation": "orchestra.perturbations",
    "CommunicationPartitionPerturbation": "orchestra.perturbations",
    "MessageCorruptionPerturbation": "orchestra.perturbations",
    "create_perturbation": "orchestra.perturbations",
    # HITL Oversight
    "HITLSupervisor": "orchestra.hitl",
    "HITLMode": "orchestra.hitl",
    "BoundaryViolation": "orchestra.hitl",
    # Analysis & Visualization
    "build_comparison_dataframe": "orchestra.analysis",
    "compute_summary_statistics": "orchestra.analysis",
    "compute_structural_performance_correlations": "orchestra.analysis",
    "generate_markdown_summary_table": "orchestra.analysis",
    "load_case_profile": "orchestra.analysis",
    "plot_communication_topology": "orchestra.analysis",
    "plot_longitudinal_evolution": "orchestra.analysis",
}


def __getattr__(name: str):
    if name in _EXPORTS:
        import importlib
        module = importlib.import_module(_EXPORTS[name])
        attr = getattr(module, name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module 'orchestra' has no attribute '{name}'")


__all__ = list(_EXPORTS.keys())
