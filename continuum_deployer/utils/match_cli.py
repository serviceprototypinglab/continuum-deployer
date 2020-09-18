import sys
from io import StringIO

from transitions import Machine
from dataclasses import dataclass, field
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text
import click

import continuum_deployer
from continuum_deployer.utils.ui import UI
from continuum_deployer.dsl.importer.helm import Helm
from continuum_deployer.resources.resources import Resources


@dataclass
class Settings:
    """Data Class that holds settings for interactive CLI."""

    # path to the resources file
    resources_path: str = field(default=None)
    resources_file: object = field(default=None)
    # path to the dsl file
    dsl_path: str = field(default=None)
    dsl_file: object = field(default=None)
    dsl_type: str = field(default=None)
    # application resources
    deployment_entities: object = field(default=None)


class DSLValidator(Validator):

    DSL_TYPES = ['helm']

    def validate(self, document):
        text = document.text

        if text not in self.DSL_TYPES:
            raise ValidationError(
                message='DSL type {} not supported, must be one of: {}'.format(text, self.DSL_TYPES))


class MatchCli:

    BANNER = """
   ____            _   _                               ____             _                       
  / ___|___  _ __ | |_(_)_ __  _   _ _   _ _ __ ___   |  _ \  ___ _ __ | | ___  _   _  ___ _ __ 
 | |   / _ \| '_ \| __| | '_ \| | | | | | | '_ ` _ \  | | | |/ _ \ '_ \| |/ _ \| | | |/ _ \ '__|
 | |__| (_) | | | | |_| | | | | |_| | |_| | | | | | | | |_| |  __/ |_) | | (_) | |_| |  __/ |   
  \____\___/|_| |_|\__|_|_| |_|\__,_|\__,_|_| |_| |_| |____/ \___| .__/|_|\___/ \__, |\___|_|   
                                                                 |_|            |___/           
   {} - Author: Daniel Hass
""".format(continuum_deployer.__version__)

    STATES = ['startup', 'input_resources', 'input_dsl', 'dsl_type']

    _TEXT_ASKRESOURCES = 'Enter path to resources file'
    _TEXT_ASKDSL = 'Enter path to DSL file'
    _TEXT_ASKDSLTYPE = 'Enter DSL type: '

    def __init__(self, resources_path, dsl_path):

        self.resources = None

        self.settings = Settings()
        # TODO implement check for cli parameters
        self.settings.resources_path = resources_path
        self.settings.dsl_path = dsl_path

        # Initialize the state machine
        self.machine = Machine(
            model=self, states=MatchCli.STATES, initial='startup')

        self.machine.add_transition(
            trigger='ask_resources', source=['startup', 'input_resources'], dest='input_resources')
        self.machine.add_transition(
            trigger='ask_dsl', source=['dsl_type', 'input_dsl'], dest='input_dsl')
        self.machine.add_transition(
            trigger='ask_dsl_type', source=['input_resources', 'dsl_type'], dest='dsl_type')

    def _open_file(self, path):
        _file = open(path, "r")
        return _file

    def _parse_resources(self):
        _resources = Resources()
        _resources.parse(self.settings.resources_file)
        self.resources = _resources.get_resources()

    def on_enter_input_resources(self):

        click.echo(click.style(self.BANNER, fg='blue'), err=False)

        _path = UI.prompt_std(self._TEXT_ASKRESOURCES)
        try:
            self.settings.resources_file = self._open_file(_path)
            self._parse_resources()

            # implementation of output via pager - https://stackoverflow.com/a/1218951
            # sys.stdout = _stdout = StringIO()

            click.echo('\n')
            for r in self.resources:
                r.print()

            # sys.stdout = sys.__stdout__
            # click.echo_via_pager(_stdout.getvalue())

            self.ask_dsl_type()
        except FileNotFoundError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.ask_resources()
        except IsADirectoryError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.ask_resources()
        except Exception as e:
            click.echo(e, err=True)
            exit(1)

    def on_enter_dsl_type(self):
        # _dsl_type = UI.prompt_std(self._TEXT_ASKDSL)

        click.echo('\n')
        html_completer = WordCompleter(['helm'])
        _dsl_type = prompt(self._TEXT_ASKDSLTYPE,
                           completer=html_completer, validator=DSLValidator())
        self.settings.dsl_type = _dsl_type
        self.ask_dsl()

    def on_enter_input_dsl(self):
        click.echo('\n')
        _path = UI.prompt_std(self._TEXT_ASKDSL)
        try:
            self.settings.dsl_file = self._open_file(_path)
            if self.settings.dsl_type == 'helm':
                helm = Helm()
                helm.parse(self.settings.dsl_file)
                self.settings.deployment_entities = helm.get_app_modules()

                click.echo('\n')
                for d in self.settings.deployment_entities:
                    d.print()
            # self.ask_dsl()
        except FileNotFoundError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.ask_dsl()
        except IsADirectoryError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.ask_dsl()
        except Exception as e:
            click.echo(e, err=True)
            exit(1)
