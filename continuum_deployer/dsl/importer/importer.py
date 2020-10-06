import click

from yapsy.IPlugin import IPlugin

from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.utils.config import Config, Setting, SettingValue


class Importer(IPlugin):
    """Interface that defines interaction with several DSL specific extractor implementations."""

    DSL_TYPES = ['helm']

    def __init__(self):
        self.app_modules = []

        self._check_requirements()

        self.config = self._gen_config()

    def _check_requirements(self):
        raise NotImplementedError

    def _gen_config(self):
        return Config([])

    def parse(self, dsl_input):
        """Handles actual parsing of DSL to internal data structures. Needs to be implemented by child."""
        raise NotImplementedError

    def get_dsl_content(self, dsl_path):
        raise NotImplementedError

    def get_app_modules(self):
        """Getter method for application modules"""
        return self.app_modules

    def get_config(self):
        """Getter for current exporter config

        :return: current exporter config object
        :rtype: :class:`continuum_deployer.utils.config.Config`
        """
        return self.config

    def reset_app_modules(self):
        """Delete already parsed app modules"""
        self.app_modules = []

    def print_app_modules(self):
        """Convenience helper that prints object representation of application modules"""
        click.echo(click.style(
            "\nList of Deployments extracted:", fg='bright_blue'))
        for module in self.app_modules:
            click.echo(str(module))
