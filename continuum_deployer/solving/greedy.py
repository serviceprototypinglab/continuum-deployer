import click

from continuum_deployer.resources.resource_entity import ResourceEntity
from continuum_deployer.solving.solver import Solver
from continuum_deployer.utils.config import Config, Setting, SettingValue


class Greedy(Solver):

    @staticmethod
    def sort_by_attr(items, attr):
        """Helper function that sorts list of items based on configurable attribute

        :param items: items to sort
        :type items: list
        :param attr: name of the attribute the sorting should be carried out with
        :type attr: str
        :return: list of sorted items
        :rtype: list
        """
        return sorted(items, key=lambda x: getattr(x, attr), reverse=True)

    @staticmethod
    def deploy_iterate(entity, resources):
        """Helper that traverses a list of resources and tries to place the given
        deploment entity on one of the resources.

        :param entity: deployment entity that should be placed
        :type entity: :class:`continuum_deployer.resources.deployment.DeploymentEntity`
        :param resources: list of resource entities that are valid targets
        :type resources: list
        :return: boolean flag representing the success of the placement attempt
        :rtype: bool
        """
        for resource in resources:
            if resource.add_deployment(entity):
                return True
        return False

    def _gen_config(self):
        return Config([
            Setting('target', [
                SettingValue(
                    'cpu', description='Sorts resources and workloads by cpu for greedy matching', default=True),
                SettingValue(
                    'memory', 'Sorts resources and workloads by memory for greedy matching'),
            ])
        ])

    def greedy_attr(self, entities, resources, attr):
        entities_sorted = Greedy.sort_by_attr(entities, attr)
        resources_sorted = Greedy.sort_by_attr(resources, attr)

        for entity in entities_sorted:
            if not Greedy.deploy_iterate(entity, resources_sorted):
                self.placement_errors.append(entity)

    def do_matching(self, deployment_entities, resources):
        """Does actual deployment to resource matching
        """

        self.greedy_attr(
            deployment_entities,
            resources,
            self.config.get_setting('target').get_value().value
        )

    def match(self):
        super(Greedy, self).match()
