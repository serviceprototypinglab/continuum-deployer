from dataclasses import dataclass, field


@dataclass
class DeploymentEntity:
    """Data Class that hold extracted values for deployments."""

    name: str = field(default=None)
    memory: float = field(default=None)
    memory_limit: float = field(default=None)
    cpu: float = field(default=None)
    cpu_limit: float = field(default=None)
    yaml: dict = field(default=None)
