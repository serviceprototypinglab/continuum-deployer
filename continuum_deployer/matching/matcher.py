import click
import sys

from continuum_deployer.deployment import DeploymentEntity
from continuum_deployer.resources.resources import Resources, ResourceEntity


class Matcher():

    def __init__(self,
                 deployment_entities: DeploymentEntity,
                 resources: Resources):
        self.deployment_entities = deployment_entities
        self.resources = resources = resources

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
    def sort_by_attr(items, attr):
        return sorted(items, key=lambda x: getattr(x, attr), reverse=True)

    @staticmethod
    def deploy_iterate(entity, resources):
        for resource in resources:
            if resource.add_deployment(entity):
                return True
        return False

    def greedy_attr(self, entities, resources, attr):
        entities_sorted = Matcher.sort_by_attr(entities, attr)
        resources_sorted = Matcher.sort_by_attr(resources, attr)

        for entity in entities_sorted:
            if not Matcher.deploy_iterate(entity, resources_sorted):
                click.echo(click.style(
                    '[Error] Deployment entity ({}) '
                    'not scheduable with greedy algorithm.'.format(
                        entity),
                    fg='red'), err=True)

    def match(self):
        """Main matcher method"""
        self.check_upper_bound(self.deployment_entities, self.resources)
        click.echo(self.sort_by_attr(self.deployment_entities, 'cpu'))
        click.echo(self.sort_by_attr(self.deployment_entities, 'memory'))

        self.greedy_attr(self.deployment_entities, self.resources, 'cpu')
        for resource in self.resources:
            resource.print()
