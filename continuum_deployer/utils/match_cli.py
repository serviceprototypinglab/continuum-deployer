# pylint: disable=no-member

import sys
import time
from io import StringIO

from transitions import Machine
from dataclasses import dataclass, field
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text, HTML, ANSI
from prompt_toolkit.shortcuts import confirm
import click

import continuum_deployer
from continuum_deployer import plugins
from continuum_deployer.utils.ui import UI
from continuum_deployer.utils.exceptions import RequirementsError, FileTypeNotSupported, ImporterError, SolverError
from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.dsl.importer.helm import Helm
from continuum_deployer.resources.resources import Resources
from continuum_deployer.solving.greedy import Greedy
from continuum_deployer.solving.sat import SAT
from continuum_deployer.dsl.exporter.exporter import Exporter
from continuum_deployer.dsl.exporter.kubernetes import Kubernetes


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
    dsl_importer: object = field(default=None)
    # application resources
    deployment_entities: object = field(default=None)
    # solver options
    solver_type: int = field(default=None)
    solver: object = field(default=None)
    # exporter options
    exporter_type: int = field(default=None)
    exporter: object = field(default=None)


class ListValidator(Validator):

    def __init__(self, list: list):
        self.validation_target = list

    def validate(self, document):
        text = document.text

        if text not in self.validation_target:
            raise ValidationError(
                message='Input {} not supported, must be one of: {}'.format(text, self.validation_target))

    @staticmethod
    def list_items_to_str(list):
        _result = []
        for item in list:
            _result.append(str(item))
        return _result


class MatchCli:

    STATES = [
        'start', 'input_resources', 'input_dsl', 'dsl_type', 'config_dsl',
        'solver_type', 'config_solver', 'matching', 'check_results', 'alter_definitions',
        'export', 'init'
    ]

    _TEXT_ASKRESOURCES = 'Enter path to resources file'
    _TEXT_ASKRESHEADLINE = 'Parsed resources: '
    _TEXT_ASKDSL = 'Enter path to DSL file'
    _TEXT_ASKDSLTYPE = 'Enter DSL type: '
    _TEXT_ASKDEPLOYHEADLINE = 'Parsed workloads: '
    _TEXT_ASKSOLVERTYPE = 'Enter Solver type: '
    _TEXT_ASKEXPORTPATH = 'Enter path to results file'
    _TEXT_ASKSTARTMATCHING = 'Do you want to start matching?'
    _TEXT_ASKMATCHINGRESHEADLINE = 'Matching results:'
    _TEXT_ASKPLACEMENTOK = 'Is placement satisfying (otherwise you are able to alter the input)?'
    _TEXT_ASKALTERRESOURCES = 'Do you want to alter your resources definition?'
    _TEXT_ASKALTERWORKLOADS = 'Do you want to alter your deployment definition?'
    _TEXT_ASKSAVERESULTS = 'Do you want to save the results to a file?'
    _TEXT_ERRORPLACEMENTS = 'The following workloads could not be scheduled'
    _TEXT_ASKEXPORTERTYPE = 'Enter Exporter type: '

    INTERACTIVE_TIMEOUT = 1.5
    CLICK_PROMPT_FG_COLOR = 'bright_blue'

    def __init__(self, resources_path, dsl_path, dsl_type):

        self.resources = None

        self.settings = Settings()
        self.settings.resources_path = resources_path
        self.settings.dsl_path = dsl_path
        self.settings.dsl_type = dsl_type

        # initialize the state machine
        self.machine = Machine(
            model=self, states=MatchCli.STATES, initial='init')

        # add transitions
        self.machine.add_transition(
            trigger='start', source=['init'], dest='start')
        self.machine.add_transition(
            trigger='ask_resources', source=['start', 'input_resources'], dest='input_resources')
        self.machine.add_transition(
            trigger='ask_dsl_type', source=['input_resources', 'dsl_type'], dest='dsl_type')
        self.machine.add_transition(
            trigger='configure_dsl', source=['input_resources', 'config_dsl'], dest='config_dsl')
        self.machine.add_transition(
            trigger='ask_dsl', source=['config_dsl', 'input_dsl'], dest='input_dsl')
        self.machine.add_transition(
            trigger='ask_solver_type', source=['input_dsl', 'solver_type'], dest='solver_type')
        self.machine.add_transition(
            trigger='configure_solver', source=['solver_type', 'config_solver'], dest='config_solver')
        self.machine.add_transition(
            trigger='start_matching', source=['alter_definitions', 'config_solver'], dest='matching')
        self.machine.add_transition(
            trigger='ask_alter', source=['check_results', 'matching'], dest='alter_definitions')
        self.machine.add_transition(
            trigger='check_results', source=['matching'], dest='check_results')
        self.machine.add_transition(
            trigger='export', source=['check_results'], dest='export')

    def _get_file_content(self, path):
        with open(path, "r") as file:
            return file.read()

    def _edit_file_with_editor(self, path):
        with open(path, 'r+') as file:
            _content = file.read()
            _content_edited = click.edit(_content)
            # check if user closed editor without saving
            if _content_edited is not None:
                # clear file content
                file.seek(0)
                file.truncate()
                # write new edited content
                file.write(_content_edited)

    def _edit_content_with_editor(self, content):
        _content = content
        _content_edited = click.edit(_content)
        # check if user closed editor without saving
        if _content_edited is not None:
            return _content_edited

        return _content

    def _read_resources_file(self):
        try:
            self.settings.resources_content = self._get_file_content(
                self.settings.resources_path)

        except FileNotFoundError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.settings.resources_path = None
            self.ask_resources()
        except IsADirectoryError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.settings.resources_path = None
            self.ask_resources()

    def _parse_resources(self):
        _resources = Resources()
        _resources.parse(self.settings.resources_content)
        self.settings.resources = _resources.get_resources()

    def _read_dsl(self):
        try:
            self.settings.dsl_content = self.settings.dsl_importer.get_dsl_content(
                self.settings.dsl_path)

        except FileNotFoundError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.settings.dsl_path = None
            self.ask_dsl()
        except IsADirectoryError as e:
            click.echo(click.style(e.strerror, fg='red'), err=True)
            self.settings.dsl_path = None
            self.ask_dsl()
        except FileTypeNotSupported as e:
            click.echo(click.style(e.message, fg='red'), err=True)
            self.settings.dsl_path = None
            self.ask_dsl()
        except ImporterError as e:
            click.echo(click.style(e.message, fg='red'), err=True)
            self.settings.dsl_path = None
            self.ask_dsl()

    def _parse_dsl(self):
        self.settings.dsl_importer.parse(self.settings.dsl_content)
        self.settings.deployment_entities = self.settings.dsl_importer.get_app_modules()

    def _ask_setting_options(self, config):

        _config = config
        for setting in _config.get_settings():
            click.echo('Configure {}:\n'.format(setting.name))
            _options = setting.get_options()
            for key, option in enumerate(_options):
                click.echo('[{}] {} - {}'.format(key,
                                                 click.style(
                                                     option.value, fg='blue'),
                                                 option.description))

            _list_of_options = list(range(len(_options)))
            _list_of_options = ListValidator.list_items_to_str(
                _list_of_options)

            option_completer = WordCompleter(_list_of_options)
            _option_choice = prompt(ANSI(click.style('\nWhich config option do you choose: ', fg=self.CLICK_PROMPT_FG_COLOR)),
                                    completer=option_completer, validator=ListValidator(_list_of_options))

            setting.set_value(_options[int(_option_choice)])

    @staticmethod
    def _options_array_to_number_choices(options):
        _options_length = len(options)
        _result = list(range(_options_length))
        _result = [format(x, 'd') for x in _result]
        return _result

    def on_enter_start(self):
        click.echo(click.style(UI.CLI_BANNER.format(
            continuum_deployer.app_version), fg='blue'), err=False)

        self.ask_resources()

    def on_enter_input_resources(self):

        if self.settings.resources_path is None:
            # resources path not already set via CLI param
            self.settings.resources_path = UI.prompt_std(
                self._TEXT_ASKRESOURCES)
            click.echo('\n')

        self._read_resources_file()
        self._parse_resources()

        # implementation of output via pager - https://stackoverflow.com/a/1218951
        # sys.stdout = _stdout = StringIO()

        click.secho(self._TEXT_ASKRESHEADLINE, fg='cyan', bold=True)
        click.echo('\n')
        for r in self.settings.resources:
            r.print()

        # sys.stdout = sys.__stdout__
        # click.echo_via_pager(_stdout.getvalue())

        self.configure_dsl()

    def on_enter_config_dsl(self):
        click.echo('\n')

        _importer = {
            'helm': Helm,
        }

        for plugin in plugins.plugin_manager.getPluginsOfCategory("Importer"):
            _name = plugin.name.lower()
            _importer[_name] = plugin.plugin_object

        _options = list(_importer.keys())

        if self.settings.dsl_type is None:
            prompt_completer = WordCompleter(_options)
            _dsl_type = prompt(ANSI(click.style(self._TEXT_ASKDSLTYPE, fg=self.CLICK_PROMPT_FG_COLOR)),
                               completer=prompt_completer, validator=ListValidator(_options))
            self.settings.dsl_type = _dsl_type

        try:
            self.settings.dsl_importer = _importer[self.settings.dsl_type]()
        except RequirementsError as e:
            click.echo(click.style(
                '\n[Error] {} '.format(e.message), fg='red'), err=True)
            exit(1)

        click.echo('\n')
        _config = self.settings.dsl_importer.get_config()
        self._ask_setting_options(_config)

        self.ask_dsl()

    def on_enter_input_dsl(self):
        click.echo('\n')

        if self.settings.dsl_path is None:
            # resources path not already set via CLI param
            self.settings.dsl_path = UI.prompt_std(self._TEXT_ASKDSL)

        self._read_dsl()
        self._parse_dsl()

        click.echo('\n')
        click.secho(self._TEXT_ASKDEPLOYHEADLINE, fg='cyan', bold=True)
        click.echo('\n')
        for d in self.settings.deployment_entities:
            d.print()

        self.ask_solver_type()

    def on_enter_solver_type(self):

        global plugins

        click.echo('\n')

        solver_chooser_text = '''
<b>Choose a solver for the workload placement:</b>
\t [0] <b>Greedy Solver</b> (sorts workloads and fills targets in a greedy fashion)
\t [1] <b>SAT Solver</b> (offers various options for mathematical optimal placements)
'''

        _solvers = [Greedy, SAT]

        for plugin in plugins.plugin_manager.getPluginsOfCategory("Solver"):
            _solvers.append(plugin.plugin_object)
            new_solver_option = '\t [{}] <b>{}</b> ({})'.format(
                len(_solvers)-1, plugin.name, plugin.description)
            solver_chooser_text = '{}{}\n'.format(
                solver_chooser_text, new_solver_option)

        print_formatted_text(HTML(solver_chooser_text))

        _options = MatchCli._options_array_to_number_choices(_solvers)

        prompt_completer = WordCompleter(_options)
        _solver_type = prompt(ANSI(click.style(self._TEXT_ASKSOLVERTYPE, fg=self.CLICK_PROMPT_FG_COLOR)),
                              completer=prompt_completer, validator=ListValidator(_options))
        self.settings.solver_type = _solver_type

        _solver = _solvers[int(self.settings.solver_type)]

        self.settings.solver = _solver(
            self.settings.deployment_entities, self.settings.resources)

        self.configure_solver()

    def on_enter_config_solver(self):
        click.echo('\n')
        click.echo('Configure solver settings:\n')

        _config = self.settings.solver.get_config()
        for setting in _config.get_settings():
            click.echo('Configure {}:\n'.format(setting.name))
            _options = setting.get_options()
            for key, option in enumerate(_options):
                click.echo('[{}] {} - {}'.format(key,
                                                 click.style(
                                                     option.value, fg='blue'),
                                                 option.description))

            _list_of_options = list(range(len(_options)))
            _list_of_options = ListValidator.list_items_to_str(
                _list_of_options)

            option_completer = WordCompleter(_list_of_options)
            _option_choice = prompt(ANSI(click.style('\nWhich config option do you choose: ', fg=self.CLICK_PROMPT_FG_COLOR)),
                                    completer=option_completer, validator=ListValidator(_list_of_options))

            setting.set_value(_options[int(_option_choice)])

        self.start_matching()

    def on_enter_matching(self):
        click.echo('\n')
        _start_matching = confirm(
            ANSI(click.style(self._TEXT_ASKSTARTMATCHING, fg=self.CLICK_PROMPT_FG_COLOR)))

        # clear already matched resources (necessary for rerun)
        self.settings.solver.reset_matching()

        if _start_matching:
            try:
                self.settings.solver.match()
            except SolverError as e:
                click.echo(click.style(e.message, fg='red'), err=True)
                self.ask_alter()

            _matched_resources = self.settings.solver.get_resources()
            click.echo('\n')
            click.secho(self._TEXT_ASKMATCHINGRESHEADLINE,
                        fg='cyan', bold=True)
            click.echo('\n')
            for r in _matched_resources:
                r.print()
                time.sleep(self.INTERACTIVE_TIMEOUT)

            _placement_errors = self.settings.solver.get_placement_errors()
            if _placement_errors:
                click.echo(click.style(
                    '\n[Error] {}: '.format(self._TEXT_ERRORPLACEMENTS), fg='red'), err=True)
                for workload in _placement_errors:
                    workload.print()
                    click.echo('\n')

            self.check_results()
        else:
            click.echo('Bye!')
            quit()

    def on_enter_check_results(self):

        _placement_ok = confirm(
            ANSI(click.style(self._TEXT_ASKPLACEMENTOK, fg=self.CLICK_PROMPT_FG_COLOR)))
        if _placement_ok:
            self.export()
        else:
            self.ask_alter()

    def on_enter_alter_definitions(self):
        click.echo('\n')

        _alter_resources = confirm(
            ANSI(click.style(self._TEXT_ASKALTERRESOURCES, fg=self.CLICK_PROMPT_FG_COLOR)))
        if _alter_resources:
            # open editor
            self._edit_file_with_editor(self.settings.resources_path)
            self._read_resources_file()
            self._parse_resources()
            self.settings.solver.set_resources(self.settings.resources)

        _alter_deployments = confirm(
            ANSI(click.style(self._TEXT_ASKALTERWORKLOADS, fg=self.CLICK_PROMPT_FG_COLOR)))
        if _alter_deployments:
            # open editor
            self.settings.dsl_content = self._edit_content_with_editor(
                self.settings.dsl_content)
            self.settings.dsl_importer.reset_app_modules()
            self._parse_dsl()
            self.settings.solver.set_deployment_entities(
                self.settings.deployment_entities)

        self.start_matching()

    def on_enter_export(self):
        click.echo('\n')

        _importer = {
            'kubernetes': Kubernetes,
        }

        for plugin in plugins.plugin_manager.getPluginsOfCategory("Exporter"):
            _name = plugin.name.lower()
            _importer[_name] = plugin.plugin_object

        _options = list(_importer.keys())

        if self.settings.exporter_type is None:
            prompt_completer = WordCompleter(_options)
            _exporter_type = prompt(ANSI(click.style(self._TEXT_ASKEXPORTERTYPE, fg=self.CLICK_PROMPT_FG_COLOR)),
                                    completer=prompt_completer, validator=ListValidator(_options))
            self.settings.exporter_type = _exporter_type

        self.settings.exporter = _importer[self.settings.exporter_type]

        click.echo('\n')
        _save_results = confirm(
            ANSI(click.style(self._TEXT_ASKSAVERESULTS, fg=self.CLICK_PROMPT_FG_COLOR)))
        if _save_results:
            click.echo('\n')
            _export_path = UI.prompt_std(self._TEXT_ASKEXPORTPATH)
            try:
                with open(_export_path, 'w') as file:
                    exporter = self.settings.exporter(output_stream=file)
                    exporter.export(self.settings.resources)
            except Exception as e:
                click.echo(click.style(e.strerror, fg='red'), err=True)
                self.export()
        else:
            exit(0)
