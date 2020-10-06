# pylint: disable=no-member

import click
import yaml

from continuum_deployer import plugins as plugins_loader
from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.dsl.importer.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.solving.solver import Solver
from continuum_deployer.solving.greedy import Greedy
from continuum_deployer.solving.sat import SAT
from continuum_deployer.dsl.exporter.exporter import Exporter
from continuum_deployer.utils.match_cli import MatchCli


_HELPTEXT_TYPE = 'Deployment DSL type'
_HELPTEXT_DSL = 'Path to DSL file'
_HELPTEXT_RESOURCES = 'Path to resources file'
_HELPTEXT_SOLVER = 'Solver to match deployments to resources'
_HELPTEXT_OUTPUT = 'Path to output file'
_HELPTEXT_PLUGINS = 'Additional plugins directory path'


@click.group()
def cli():
    """
    Prototypical Continuum Computing Deployer\n
    Authors: Daniel Hass
    """
    pass


@cli.command()
@click.option('-f', '--file', required=True, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(Importer.DSL_TYPES), default='helm', help=_HELPTEXT_TYPE)
def print_deployments(file, type):
    """Parses deployments and prints result"""

    stream = open(file, 'r')

    if type == 'helm':
        helm = Helm()
        helm.parse(stream)
        helm.print_app_modules()
    else:
        raise NotImplementedError


@cli.command()
@click.option('-f', '--file', required=True, help=_HELPTEXT_RESOURCES)
def print_resources(file):
    """Parses resources YAML and prints result"""

    stream = open(file, 'r')
    resources = Resources()
    resources.parse(stream)
    resources.print_resources()


@cli.command()
@click.option('-r', '--resources', required=False, default=None, help=_HELPTEXT_RESOURCES)
@click.option('-d', '--deployment', required=False, default=None, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(Importer.DSL_TYPES), default=None, show_default=True, help=_HELPTEXT_TYPE)
@click.option('-p', '--plugins', type=str, default=None, show_default=True, help=_HELPTEXT_PLUGINS)
def match(resources, deployment, type, plugins):
    """
    Match deployments interactively
    """

    if plugins != None:
        plugins_loader.add_plugins_path(plugins)
        plugins_loader.load_plugins()

    match_cli = MatchCli(resources, deployment, type)
    match_cli.start()


if __name__ == "__main__":
    cli()
