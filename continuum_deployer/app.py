import click

from continuum_deployer.extractors.helm import Helm


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


if __name__ == "__main__":
    cli()
