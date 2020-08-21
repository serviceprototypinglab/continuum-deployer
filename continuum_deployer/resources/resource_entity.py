from dataclasses import dataclass, field


@dataclass
class ResourceEntity:
    """Data Class that hold extracted values for resources."""

    name: str = field(default=None)
    memory: float = field(default=None)
    cpu: float = field(default=None)
