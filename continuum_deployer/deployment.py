from dataclasses import dataclass, field


@dataclass
class DeploymentEntity:
    """Data Class that hold extracted values for deployments."""

    name: str = field(default=None)
    resources_requests: dict = field(default=None)
    resources_limits: dict = field(default=None)
