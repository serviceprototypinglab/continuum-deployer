import click
import yaml

from continuum_deployer.extractors.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.matching.matcher import Matcher
from continuum_deployer.matching.greedy import Greedy
from continuum_deployer.matching.sat import SAT
from continuum_deployer.exporter import Exporter


_HELPTEXT_TYPE = 'Deployment DSL type'
_HELPTEXT_DSL = 'Path to DSL file'
_HELPTEXT_RESOURCES = 'Path to resources file'
_HELPTEXT_SOLVER = 'Solver to match deployments to resources'
_HELPTEXT_OUTPUT = 'Path to output file'


@click.group()
def cli():
    """Prototypical Continuum Computing Deployer"""
    pass


@cli.command()
@click.option('-f', '--file', required=True, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(['helm']), default='helm', help=_HELPTEXT_TYPE)
def print_resources(file, type):

    stream = open(file, 'r')

    if type == 'helm':
        helm = Helm()
        helm.parse(stream)
        helm.print_app_modules()
    else:
        raise NotImplementedError


@cli.command()
@click.option('-f', '--file', required=True, help=_HELPTEXT_RESOURCES)
def parse_resources(file):
    """Parses the resources YAML and prints all extracted resource entities"""

    stream = open(file, 'r')
    resources = Resources()
    resources.parse(stream)
    resources.print_resources()


@cli.command()
@click.option('-r', '--resources', required=True, help=_HELPTEXT_RESOURCES)
@click.option('-d', '--deployment', required=True, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(['helm']), default='helm', show_default=True, help=_HELPTEXT_TYPE)
@click.option('-s', '--solver', type=click.Choice(['sat', 'greedy']), default='sat', show_default=True, help=_HELPTEXT_SOLVER)
@click.option('-o', '--output', 'output_path', type=str, help=_HELPTEXT_OUTPUT)
def match(resources, deployment, type, solver, output_path):
    """
        Matches the given deployments with the available resources
        using the specified solver.
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


if __name__ == "__main__":
    cli()
