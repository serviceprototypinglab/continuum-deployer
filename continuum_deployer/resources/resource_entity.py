from dataclasses import dataclass, field
from typing import List
import click

from continuum_deployer.deployment import DeploymentEntity


@dataclass
class ResourceEntity:
    """Data Class that hold extracted values for resources."""

    name: str = field(default=None)
    memory: float = field(default=None)
    cpu: float = field(default=None)
    deployments: List[DeploymentEntity] = field(default_factory=list)

    def check_resources_fit(self, entity):
        avaiable_cpu = self.cpu
        avaiable_memory = self.memory
        deployments_proposal = self.deployments + [entity]
        for deployment in deployments_proposal:
            avaiable_cpu -= deployment.cpu
            avaiable_memory -= deployment.memory

        if avaiable_memory >= 0 and avaiable_cpu >= 0:
            return True
        else:
            return False

    def add_deployment(self, entity):
        if self.check_resources_fit(entity):
            self.deployments.append(entity)
            return True
        else:
            return False

    def print(self):
        click.echo("NAME: {}".format(self.name))
        click.echo("CPU: {}".format(self.cpu))
        click.echo("MEMORY: {}".format(self.memory))
        click.echo("DEPLOYMENTS: {}".format(self.deployments))
        click.echo("---")
