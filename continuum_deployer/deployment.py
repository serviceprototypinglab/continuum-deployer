from dataclasses import dataclass, field


@dataclass
class DeploymentEntity:
    """Data Class that holds extracted values for deployments."""

    # name of the deployment
    name: str = field(default=None)
    # amount of memory the deployment requires to run
    memory: float = field(default=None)
    # amount of memory the deployment is allowed to use at max
    # TODO - not implemented
    memory_limit: float = field(default=None)
    # amount of cpu resources the deployment requires to run
    # 1=1 cpu core | 0.5=0.5 cpu core
    cpu: float = field(default=None)
    # number of cpu cores the deployment is allowed to use at max
    # TODO - no implemented
    cpu_limit: float = field(default=None)
    # raw extracted yaml definition
    yaml: dict = field(default=None)
    # assigned labels
    labels: dict = field(default=None)
