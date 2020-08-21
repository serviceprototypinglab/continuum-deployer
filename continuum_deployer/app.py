import click

from continuum_deployer.extractors.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.matching.matcher import Matcher


@click.group()
def cli():
    pass


@cli.command()
@click.option('-f', '--file', required=True, help='Path to DSL file')
@click.option('-t', '--type', type=click.Choice(['helm']), default='helm')
def print_resources(file, type):

    stream = open(file, 'r')

    if type == 'helm':
        helm = Helm()
        helm.parse(stream)
        helm.print_app_modules()
    else:
        raise NotImplementedError


@cli.command()
@click.option('-f', '--file', required=True, help='Path to resources file')
def parse_resources(file):

    stream = open(file, 'r')
    resources = Resources()
    resources.parse(stream)
    resources.print_resources()


@cli.command()
@click.option('-r', '--resources', required=True, help='Path to resources file')
@click.option('-d', '--deployment', required=True, help='Path to deployment DSL file')
@click.option('-t', '--type', type=click.Choice(['helm']), default='helm')
def match(resources, deployment, type):

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

    matcher = Matcher(deployment_entities, resources.get_resources())
    matcher.match()


if __name__ == "__main__":
    cli()
