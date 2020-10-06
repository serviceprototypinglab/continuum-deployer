# pylint: disable=no-member

import click

from continuum_deployer import plugins as plugins_loader
from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.dsl.importer.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.utils.match_cli import MatchCli


_HELPTEXT_TYPE = 'Type of helm definition'
_HELPTEXT_DSL = 'Path to Helm definition'
_HELPTEXT_RESOURCES = 'Path to resources file'
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
@click.option('-p', '--path', required=True, help=_HELPTEXT_DSL)
@click.option('-t', '--type', type=click.Choice(['yaml', 'chart']), default='yaml', help=_HELPTEXT_TYPE)
def parse_helm(path, type):
    """Parses helm deployment definitions and prints result"""

    helm = Helm()
    config = helm.get_config()
    _setting = next(x for x in config.get_settings()
                    if x.name == 'chart_origin')

    if type == 'yaml':
        _setting.set_value(
            next(x for x in _setting.get_options() if x.value == 'yaml'))
    elif type == 'chart':
        _setting.set_value(
            next(x for x in _setting.get_options() if x.value == 'chart'))
    else:
        raise NotImplementedError

    _dsl = helm.get_dsl_content(path)
    helm.parse(_dsl)
    helm.print_app_modules()


@cli.command()
@click.option('-f', '--file', required=True, help=_HELPTEXT_RESOURCES)
def parse_resources(file):
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
    """Match deployments interactively"""

    if plugins != None:
        plugins_loader.add_plugins_path(plugins)
        plugins_loader.load_plugins()

    match_cli = MatchCli(resources, deployment, type)
    match_cli.start()


if __name__ == "__main__":
    cli()
