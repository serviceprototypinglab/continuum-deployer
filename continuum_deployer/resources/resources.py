import yaml
import click


class Resources:

    MANDATORY_FIELDS = ['name', 'cpu', 'ram']

    def __init__(self):
        pass

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
            click.echo("NAME: {}".format(node.get('name')))
            click.echo("CPU: {}".format(node.get('cpu')))
            click.echo("RAM: {}".format(node.get('ram')))
