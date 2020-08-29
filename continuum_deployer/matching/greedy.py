import click

from continuum_deployer.resources.resource_entity import ResourceEntity
from continuum_deployer.matching.matcher import Matcher


class Greddy(Matcher):

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
        entities_sorted = Greddy.sort_by_attr(entities, attr)
        resources_sorted = Greddy.sort_by_attr(resources, attr)

        for entity in entities_sorted:
            if not Greddy.deploy_iterate(entity, resources_sorted):
                click.echo(click.style(
                    '[Error] Deployment entity ({}) '
                    'not scheduable with greedy algorithm.'.format(
                        entity),
                    fg='red'), err=True)

    def match(self):
        super(Greddy, self).match()

        self.greedy_attr(self.deployment_entities, self.resources, 'cpu')
        for resource in self.resources:
            resource.print()
