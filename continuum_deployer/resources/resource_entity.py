from dataclasses import dataclass, field
from typing import List
import click

from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.utils.ui import UI


@dataclass
class ResourceEntity:
    """Data Class that hold extracted values for resources."""

    name: str = field(default=None)
    memory: float = field(default=None)
    cpu: float = field(default=None)
    deployments: List[DeploymentEntity] = field(default_factory=list)
    labels: dict = field(default=None)

    def check_resources_fit(self, entity):
        """Idempotent helper method that checks if given deployment entity 
        can be added to the resource without exceeding the limits.

        :param entity: deployment entity whose fit should be tested
        :type entity: :class:`continuum_deployer.resources.deployment.DeploymentEntity`
        :return: Check result if deployment entity cloud be placed as boolean
        :rtype: bool
        """
        available_cpu = self.cpu
        available_memory = self.memory
        deployments_proposal = self.deployments + [entity]
        for deployment in deployments_proposal:
            available_cpu -= deployment.cpu
            available_memory -= deployment.memory

        if available_memory >= 0 and available_cpu >= 0:
            return True
        else:
            return False

    def add_deployment(self, entity):
        """Add new deployment entity to current resource.

        :param entity: deployment entity that should be added
        :type entity: :class:`continuum_deployer.resources.deployment.DeploymentEntity`
        :return: result of add operation
        :rtype: bool
        """
        if self.check_resources_fit(entity):
            self.deployments.append(entity)
            return True
        else:
            return False

    def print(self):
        """Helper method that prints resource entity parameters and current deployments to stdout
        """

        click.echo(click.style("Name: {}".format(self.name), fg='bright_blue'))
        click.echo(click.style("CPU: {} \t MEMORY: {} MB".format(
            self.cpu, self.memory
        ), fg=None))
        UI.print_percent_bar('CPU', (sum(d.cpu for d in self.deployments)/self.cpu) * 100
                             if len(self.deployments) != 0 else 0)
        UI.print_percent_bar('RAM', (sum(d.memory for d in self.deployments)/self.memory) * 100
                             if len(self.deployments) != 0 else 0)
        _printed_deployments = "\n"
        for deployment in self.deployments:
            _printed_deployments += "\t {}, cpu={}, memory={}, label=[{}] \n".format(
                deployment.name, deployment.cpu, deployment.memory, UI.pretty_label_string(
                    deployment.labels)
            )
        click.echo("DEPLOYMENTS: {}".format(_printed_deployments.rstrip("\n")))
        click.echo("LABEL: {}".format(UI.pretty_label_string(self.labels)))
        click.echo("-----------------------------------------")

    def get_deployments(self):
        return self.deployments

    def get_idle_cpu(self):
        return self.cpu - sum(d.cpu for d in self.deployments)

    def get_idle_memory(self):
        return self.memory - sum(d.memory for d in self.deployments)

    def clear_deployments(self):
        """ Removes all placed deployments
        """

        self.deployments = []
