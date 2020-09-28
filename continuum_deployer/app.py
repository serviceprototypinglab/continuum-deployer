# pylint: disable=no-member

import click
import yaml

from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.dsl.importer.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.matching.matcher import Matcher
from continuum_deployer.matching.greedy import Greedy
from continuum_deployer.matching.sat import SAT
from continuum_deployer.dsl.exporter.exporter import Exporter
from continuum_deployer.utils.match_cli import MatchCli


_HELPTEXT_TYPE = 'Deployment DSL type'
_HELPTEXT_DSL = 'Path to DSL file'
_HELPTEXT_RESOURCES = 'Path to resources file'
_HELPTEXT_SOLVER = 'Solver to match deployments to resources'
_HELPTEXT_OUTPUT = 'Path to output file'


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
@click.option('-r', '--resources', required=True, help=_HELPTEXT_RESOURCES)
@click.option('-d', '--deployment', required=True, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(Importer.DSL_TYPES), default='helm', show_default=True, help=_HELPTEXT_TYPE)
@click.option('-s', '--solver', type=click.Choice(['sat', 'greedy']), default='sat', show_default=True, help=_HELPTEXT_SOLVER)
@click.option('-o', '--output', 'output_path', type=str, help=_HELPTEXT_OUTPUT)
def nonint_match(resources, deployment, type, solver, output_path):
    """
        Match deployments non-interactively using cli parameters
    """

    _deployment_file = open(deployment, 'r')

    deployment_entities = None
    if type == 'helm':
        helm = Helm()
        helm.parse(_deployment_file)
        deployment_entities = helm.get_app_modules()
    else:
        raise NotImplementedError

    _resources_file = open(resources, 'r')
    resources = Resources()
    resources.parse(_resources_file)

    if solver == 'sat':
        matcher = SAT(deployment_entities, resources.get_resources())
    elif solver == 'greedy':
        matcher = Greedy(deployment_entities, resources.get_resources())
    matcher.match()
    matcher.print_resources()

    resources_matched = matcher.get_resources()

    file = None

    if output_path is None:
        exporter = Exporter(stdout=True)
    else:
        file = open(output_path, "w")
        exporter = Exporter(output_stream=file)
    exporter.export(resources_matched)

    if file is not None:
        file.close()


@cli.command()
@click.option('-r', '--resources', required=False, default=None, help=_HELPTEXT_RESOURCES)
@click.option('-d', '--deployment', required=False, default=None, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(Importer.DSL_TYPES), default=None, show_default=True, help=_HELPTEXT_TYPE)
def match(resources, deployment, type):
    """
    Match deployments interactively
    """

    match_cli = MatchCli(resources, deployment, type)
    match_cli.start()


if __name__ == "__main__":
    cli()
