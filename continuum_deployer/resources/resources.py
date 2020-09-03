import yaml
import click

from continuum_deployer.resources.resource_entity import ResourceEntity


class Resources:

    MANDATORY_FIELDS = ['name', 'cpu', 'memory']

    def __init__(self):
        self.resources = list()

    def check_mandatory_fields(self, node):
        for field in self.MANDATORY_FIELDS:
            if field not in node:
                click.echo(click.style(
                    '[Error] Malformed resource definition. Missing '
                    'required field {}.'.format(field), fg='red'), err=True)
                exit(1)

    def parse(self, definiton):
        # see default loader deprication
        # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
        nodes = yaml.load(definiton, Loader=yaml.SafeLoader)['resources']

        for node in nodes:
            self.check_mandatory_fields(node)
            _resource = ResourceEntity()
            _resource.name = node.get('name')
            _resource.memory = node.get('memory')
            _resource.cpu = node.get('cpu')
            _resource.labels = node.get('labels', None)
            self.resources.append(_resource)

    def print_resources(self):
        for entity in self.resources:
            entity.print()

    def get_resources(self):
        return self.resources
