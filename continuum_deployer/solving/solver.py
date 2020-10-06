import click
import sys

from yapsy.IPlugin import IPlugin

from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.resources.resources import Resources, ResourceEntity
from continuum_deployer.utils.config import Config, Setting, SettingValue
from continuum_deployer.utils.exceptions import SolverError


class Solver(IPlugin):

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
        """Generates the default configuration for the solver

        :return: generated default config
        :rtype: :class:`continuum_deployer.utils.config.Config`
        """
        return Config([])

    def get_config(self):
        """Getter for current solver config

        :return: current solver config
        :rtype: :class:`continuum_deployer.utils.config.Config`
        """
        return self.config

    def set_config_value(self, value):
        """Setter that overwrites or adds a specific solver config value

        :param value: setting to change or overwrite
        :type value: :class:`continuum_deployer.utils.config.Setting`
        """
        self.config.add_setting(value)

    def check_upper_bound(self, entities, resources):
        """Helper that iterates all deployment and resources entities to check
        if a certain deployment exceeds the largest available resource.

        :param entities: list of deployment entities
        :type entities: list
        :param resources: list of resource entities
        :type resources: list
        :raises SolverError: raised if largest deployment exceeds available resources
        """

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
            _error_msg = ('[Error] Smallest deployable unit memory request ({}) '
                          'exceeds largest target size ({}).').format(
                _max_memory_request, _max_memory_offer
            )
            raise SolverError(message=_error_msg)

        # check if max cpu fits available resources
        if _max_cpu_offer < _max_cpu_request:
            _error_msg = ('[Error] Smallest deployable unit cpu request ({}) '
                          'exceeds largest target size ({}).').format(
                _max_cpu_request, _max_cpu_offer
            )
            raise SolverError(message=_error_msg)

    @staticmethod
    def _tokenize_labels(labels: dict):
        """Helper function that hashes a dict of labels

        :param labels: labels that should be hashed
        :type labels: dict
        :return: hashed labels
        :rtype: str
        """
        # hash dict of labels to make grouping easier
        _result = hash(frozenset(labels.items()))
        return _result

    @staticmethod
    def _token_exists_or_create(data, token):
        """Helper function that initializes key in dict with empty array if it doesn't exist

        :param data: dict to work on
        :type data: dict
        :param token: key to initialize if not existing
        :type token: str
        :return: altered dict
        :rtype: dict
        """
        if token not in data:
            data[token] = []
        return data

    def _get_suitable_resources(self, resources, labels):
        """Helper function that returns resources that have all of the given resources

        :param resources: list of resources to filter or check against labels
        :type resources: list
        :param labels: labels that are base for the filtering
        :type labels: dict
        :return: list of resources that have all given labels assigned to them
        :rtype: list
        """
        _suitable_resources = []
        for resource in resources:
            if resource.labels is not None:
                if labels.items() <= resource.labels.items():
                    _suitable_resources.append(resource)
        return _suitable_resources

    def group(self, entities):
        """Helper function that creates a dict datastructure containing
        groups of elements that have the same labels assigned

        :param entities: list of items to group
        :type entities: list
        :return: grouped dict datastructure, keys are based on label hashes
        :rtype: dict
        """
        _grouping = dict()

        for entity in entities:
            if entity.labels is None:
                # entity is unlabeled
                _grouping = Solver._token_exists_or_create(
                    _grouping, self.UNLABELED_TOKEN)
                _grouping[self.UNLABELED_TOKEN].append(entity)
            else:
                # entity is labeled
                _token = Solver._tokenize_labels(entity.labels)
                _grouping = Solver._token_exists_or_create(_grouping, _token)
                _grouping[_token].append(entity)
        return _grouping

    def do_matching(self, deployment_entities, resources):
        """Does actual deployment to resource matching
        """
        raise NotImplementedError

    def match(self):
        """Main matcher method that invokes some preflight checks
        and starts the label based grouped matching
        """
        self.check_upper_bound(self.deployment_entities, self.resources)
        self.match_labeled()

    def match_labeled(self):
        """Handles group based label matching. Functions calls actual solver implementation do_matching()
        multiple times and takes care of the deployment constrains enforced by the assigned labels.
        """
        self.grouped_deployments = self.group(self.deployment_entities)
        self.grouped_resources = self.group(self.resources)

        _unlabeled_deployments = []

        if self.UNLABELED_TOKEN in self.grouped_deployments:
            _unlabeled_deployments = self.grouped_deployments.pop(
                self.UNLABELED_TOKEN)

        for token in sorted(self.grouped_deployments.keys()):
            # get group labels in dict form, first can be taken as they are equal throwout a group
            _group_labels = self.grouped_deployments[token][0].labels

            _suitable_resources = self._get_suitable_resources(
                self.resources, _group_labels)

            self.do_matching(
                self.grouped_deployments[token], _suitable_resources)

        # match unlabeled deployments
        self.do_matching(
            _unlabeled_deployments, self.resources)

    def reset_matching(self):
        """Resets current matching state of solver
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
