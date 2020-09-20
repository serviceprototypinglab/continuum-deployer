# pylint: disable=no-member

import sys
from io import StringIO

from transitions import Machine
from dataclasses import dataclass, field
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import confirm
import click

import continuum_deployer
from continuum_deployer.utils.ui import UI
from continuum_deployer.dsl.importer.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.matching.greedy import Greedy
from continuum_deployer.matching.sat import SAT


@dataclass
class Settings:
    """Data Class that holds settings for interactive CLI."""

    # path to the resources file
    resources_path: str = field(default=None)
    resources_content: object = field(default=None)
    resources: object = field(default=None)
    # path to the dsl file
    dsl_path: str = field(default=None)
    dsl_content: object = field(default=None)
    dsl_type: str = field(default=None)
    # application resources
    deployment_entities: object = field(default=None)
    # solver options
    solver_type: int = field(default=None)
    solver: object = field(default=None)


class DSLValidator(Validator):

    DSL_TYPES = ['helm']

    def validate(self, document):
        text = document.text

        if text not in self.DSL_TYPES:
            raise ValidationError(
                message='DSL type {} not supported, must be one of: {}'.format(text, self.DSL_TYPES))


class SolverValidator(Validator):

    SOLVER_TYPES = ['1', '2']

    def validate(self, document):
        text = document.text

        if text not in self.SOLVER_TYPES:
            raise ValidationError(
                message='Solver type {} not supported, must be one of: {}'.format(text, self.SOLVER_TYPES))


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

    STATES = ['startup', 'input_resources',
              'input_dsl', 'dsl_type', 'solver_type', 'matching', 'alter_definitions']

    _TEXT_ASKRESOURCES = 'Enter path to resources file'
    _TEXT_ASKDSL = 'Enter path to DSL file'
    _TEXT_ASKDSLTYPE = 'Enter DSL type: '
    _TEXT_ASKSOLVERTYPE = 'Enter Solver type: '

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
            trigger='ask_dsl_type', source=['input_resources', 'dsl_type'], dest='dsl_type')
        self.machine.add_transition(
            trigger='ask_dsl', source=['dsl_type', 'input_dsl'], dest='input_dsl')
        self.machine.add_transition(
            trigger='ask_solver_type', source=['input_dsl', 'solver_type'], dest='solver_type')
        self.machine.add_transition(
            trigger='start_matching', source=['solver_type'], dest='matching')
        self.machine.add_transition(
            trigger='ask_alter', source=['matching'], dest='alter_definitions')

    def _get_file_content(self, path):
        with open(path, "r") as file:
            return file.read()

    def _edit_file_with_editor(self, path):
        with open(path, 'r+') as file:
            _content = file.read()
            _content_edited = click.edit(_content)
            if _content_edited is not None:
                # clear file content
                file.seek(0)
                file.truncate()
                # write new edited content
                file.write(_content_edited)

    def on_enter_input_resources(self):

        click.echo(click.style(self.BANNER, fg='blue'), err=False)

        self.settings.resources_path = UI.prompt_std(self._TEXT_ASKRESOURCES)
        try:
            self.settings.resources_content = self._get_file_content(
                self.settings.resources_path)

            _resources = Resources()
            _resources.parse(self.settings.resources_content)
            self.settings.resources = _resources.get_resources()

            # implementation of output via pager - https://stackoverflow.com/a/1218951
            # sys.stdout = _stdout = StringIO()

            click.echo('\n')
            for r in self.settings.resources:
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
        self.settings.dsl_path = UI.prompt_std(self._TEXT_ASKDSL)
        try:
            self.settings.dsl_content = self._get_file_content(
                self.settings.dsl_path)
            if self.settings.dsl_type == 'helm':
                helm = Helm()
                helm.parse(self.settings.dsl_content)
                self.settings.deployment_entities = helm.get_app_modules()

                click.echo('\n')
                for d in self.settings.deployment_entities:
                    d.print()
            self.ask_solver_type()
        except FileNotFoundError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.ask_dsl()
        except IsADirectoryError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.ask_dsl()
        except Exception as e:
            click.echo(e, err=True)
            exit(1)

    def on_enter_solver_type(self):
        click.echo('\n')

        # TODO maybe read solvers dynamically
        print_formatted_text(HTML('''
<b>Choose a solver for the workload placement:</b>
\t - <b>Greedy Solver</b> (sorts workloads and fills targets in a greedy fashion) \t[1]
\t - <b>SAT Solver</b> (offers various options for mathematical optimal placements) \t[2]
'''))

        html_completer = WordCompleter(['1', '2'])
        _solver_type = prompt(self._TEXT_ASKSOLVERTYPE,
                              completer=html_completer, validator=SolverValidator())
        self.settings.solver_type = _solver_type

        if self.settings.solver_type == '1':
            self.settings.solver = Greedy(
                self.settings.deployment_entities, self.settings.resources)
        elif self.settings.solver_type == '2':
            self.settings.solver = SAT(
                self.settings.deployment_entities, self.settings.resources)
        else:
            # should never be reached due to SolverValidator
            raise Exception("Solver type not supported")

        self.start_matching()

    def on_enter_matching(self):
        click.echo('\n')

        _start_matching = confirm("Do you want to start matching?")
        if _start_matching:
            self.settings.solver.match()
            _matched_resources = self.settings.solver.get_resources()
            click.echo('\n')
            for r in _matched_resources:
                r.print()

            self.ask_alter()
        else:
            click.echo('Bye!')
            quit()

    def on_enter_alter_definitions(self):
        click.echo('\n')

        _alter_resources = confirm(
            "Do you want to alter your resources definition?")
        if _alter_resources:
            # open editor
            self._edit_file_with_editor(self.settings.resources_path)

        _alter_deployments = confirm(
            "Do you want to alter your deployment definition?")
        if _alter_deployments:
            # open editor
            self._edit_file_with_editor(self.settings.dsl_path)
