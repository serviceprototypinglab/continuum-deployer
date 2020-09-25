import click

from continuum_deployer.resources.resource_entity import ResourceEntity
from continuum_deployer.matching.matcher import Matcher
from continuum_deployer.utils.config import Config, Setting, SettingValue


class Greedy(Matcher):

    @staticmethod
    def sort_by_attr(items, attr):
        return sorted(items, key=lambda x: getattr(x, attr), reverse=True)

    @staticmethod
    def deploy_iterate(entity, resources: ResourceEntity):
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
        """
        Does actual deployment to resource matching

        :return matched resources with assigned deployments
        """

        self.greedy_attr(
            deployment_entities,
            resources,
            self.config.get_setting('target').get_value().value
        )

    def match(self):
        super(Greedy, self).match()
