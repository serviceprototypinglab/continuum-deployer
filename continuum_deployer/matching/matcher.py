import click
import sys

from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.resources.resources import Resources, ResourceEntity
from continuum_deployer.matching.config import MatcherConfig, MatcherSetting, MatcherSettingValue


class Matcher():

    UNLABELED_TOKEN = 'unlabeled'

    def __init__(self,
                 deployment_entities: DeploymentEntity,
                 resources: Resources):
        self.deployment_entities = deployment_entities
        self.resources = resources
        self.grouped_deployments = None
        self.grouped_resources = None
        self.placement_errors = []

        self.config = self._gen_config()

    def _gen_config(self):
        return MatcherConfig([])

    def get_config(self):
        return self.config

    def set_config_value(self, value):
        self.config.add_setting(value)

    def check_upper_bound(self, entities, resources):
        # find max of resource requests on deployment entities
        _max_memory_request = 0
        _max_cpu_request = 0
        for entity in entities:
            if entity.memory > _max_memory_request:
                _max_memory_request = entity.memory
            if entity.cpu > _max_cpu_request:
                _max_cpu_request = entity.cpu

        # find max of available resources on deployment targets
        _max_memory_offer = 0
        _max_cpu_offer = 0
        for resource in resources:
            if resource.memory > _max_memory_offer:
                _max_memory_offer = resource.memory
            if resource.cpu > _max_cpu_offer:
                _max_cpu_offer = resource.cpu

        # check if max memory entity fits available resources
        if _max_memory_offer < _max_memory_request:
            click.echo(click.style(
                '[Error] Smallest deployable unit memory request ({}) '
                'exceeds largest target size ({}).'.format(
                    _max_memory_request, _max_memory_offer),
                fg='red'), err=True)
            raise Exception

        # check if max cpu fits available resources
        if _max_cpu_offer < _max_cpu_request:
            click.echo(click.style(
                '[Error] Smallest deployable unit cpu request ({}) '
                'exceeds largest target size ({}).'.format(
                    _max_cpu_request, _max_cpu_offer),
                fg='red'), err=True)
            raise Exception

    @staticmethod
    def _tokenize_label(label: dict):
        _first_key = list(label)[0]
        return '{}-{}'.format(_first_key, label.get(_first_key))

    @staticmethod
    def _token_exists_or_create(data, token):
        if token not in data:
            data[token] = []
        return data

    def group(self, entities):
        _grouping = dict()

        for entity in entities:
            if entity.labels is None:
                # entity is unlabeled
                _grouping = Matcher._token_exists_or_create(
                    _grouping, self.UNLABELED_TOKEN)
                _grouping[self.UNLABELED_TOKEN].append(entity)
            else:
                # entity is labeled
                _first_key = list(entity.labels)[0]
                _token = Matcher._tokenize_label(
                    {_first_key: entity.labels[_first_key]})
                _grouping = Matcher._token_exists_or_create(_grouping, _token)
                _grouping[_token].append(entity)
        return _grouping

    def do_matching(self, deployment_entities, resources):
        """
        Does actual deployment to resource matching
        """
        raise NotImplementedError

    def match(self):
        """Main matcher method"""
        self.check_upper_bound(self.deployment_entities, self.resources)
        self.match_labeled()

    def match_labeled(self):
        self.grouped_deployments = self.group(self.deployment_entities)
        self.grouped_resources = self.group(self.resources)

        # TODO: check if all deployment labels exist in on resources side

        if self.UNLABELED_TOKEN in self.grouped_deployments:
            _unlabeled_deployments = self.grouped_deployments.pop(
                self.UNLABELED_TOKEN)
        if self.UNLABELED_TOKEN in self.grouped_resources:
            _leftover_resources = self.grouped_resources.pop(
                self.UNLABELED_TOKEN)

        for token in sorted(self.grouped_deployments.keys()):
            self.do_matching(
                self.grouped_deployments[token], self.grouped_resources[token])
            _leftover_resources.extend(self.grouped_resources[token])

        self.do_matching(
            _unlabeled_deployments, _leftover_resources)

    def reset_matching(self):
        """Reset matching state of matcher
        """

        for resource in self.resources:
            resource.clear_deployments()

        self.grouped_deployments = None
        self.grouped_resources = None
        self.placement_errors = []

    def print_resources(self):
        for res in self.resources:
            res.print()

    def get_resources(self):
        return self.resources

    def set_resources(self, resources):
        self.resources = resources

    def get_placement_errors(self):
        return self.placement_errors

    def get_deployment_entities(self):
        return self.deployment_entities

    def set_deployment_entities(self, deployments):
        self.deployment_entities = deployments
