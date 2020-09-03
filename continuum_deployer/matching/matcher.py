import click
import sys

from continuum_deployer.deployment import DeploymentEntity
from continuum_deployer.resources.resources import Resources, ResourceEntity


class Matcher():

    def __init__(self,
                 deployment_entities: DeploymentEntity,
                 resources: Resources):
        self.deployment_entities = deployment_entities
        self.resources = resources

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

    def match(self):
        """Main matcher method"""
        self.check_upper_bound(self.deployment_entities, self.resources)

    def print_resources(self):
        for res in self.resources:
            res.print()

    def get_resources(self):
        return self.resources

    def get_deployment_entities(self):
        return self.deployment_entities
