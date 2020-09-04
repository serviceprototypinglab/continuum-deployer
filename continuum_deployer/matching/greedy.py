import click

from continuum_deployer.resources.resource_entity import ResourceEntity
from continuum_deployer.matching.matcher import Matcher


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

    def greedy_attr(self, entities, resources, attr):
        entities_sorted = Greedy.sort_by_attr(entities, attr)
        resources_sorted = Greedy.sort_by_attr(resources, attr)

        for entity in entities_sorted:
            if not Greedy.deploy_iterate(entity, resources_sorted):
                click.echo(click.style(
                    '[Error] Deployment entity ({}) '
                    'not scheduable with greedy algorithm.'.format(
                        entity),
                    fg='red'), err=True)

    def do_matching(self, deployment_entities, resources):
        """
        Does actual deployment to resource matching

        :return matched resources with assigned deployments
        """

        self.greedy_attr(deployment_entities, resources, 'cpu')

    def match(self):
        super(Greedy, self).match()
