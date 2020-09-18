from dataclasses import dataclass, field
import click

from continuum_deployer.utils.ui import UI


@dataclass
class DeploymentEntity:
    """Data Class that holds extracted values for deployments."""

    # name of the deployment
    name: str = field(default=None)
    # amount of memory the deployment requires to run
    memory: int = field(default=0)
    # amount of memory the deployment is allowed to use at max
    # TODO - not implemented
    memory_limit: int = field(default=0)
    # amount of cpu resources the deployment requires to run
    # 1=1 cpu core | 0.5=0.5 cpu core
    cpu: float = field(default=0)
    # number of cpu cores the deployment is allowed to use at max
    # TODO - no implemented
    cpu_limit: float = field(default=0)
    # raw extracted yaml definition
    yaml: dict = field(default=None)
    # assigned labels
    labels: dict = field(default=None)

    def print(self):
        click.echo(click.style("Name: {}".format(self.name), fg='bright_blue'))
        click.echo(click.style("CPU: {} \t MEMORY: {} MB".format(
            self.cpu, self.memory
        ), fg=None))
        click.echo("LABEL: {}".format(UI.pretty_label_string(self.labels)))
        click.echo("-----------------------------------------")
