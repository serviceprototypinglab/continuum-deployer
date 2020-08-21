import yaml
import json
import click

from continuum_deployer.extractors.extractor import Extractor
from continuum_deployer.deployment import DeploymentEntity


class Helm(Extractor):

    # TODO add support for plain Pods - requires change in parse()
    K8S_OBJECTS = ['Deployment', 'ReplicaSet',
                   'StatefulSet', 'DaemonSet', 'Jobs', 'CronJob']

    def parse(self, dsl_input):

        # see default loader deprication
        # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
        docs = yaml.load_all(dsl_input, Loader=yaml.SafeLoader)

        for doc in docs:
            if doc['kind'] in self.K8S_OBJECTS:

                # TODO add support for >1 scaled deployments
                deployment = DeploymentEntity()
                _name = doc.get('metadata', None).get('name', None)
                if _name != None:
                    deployment.name = _name
                else:
                    # https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
                    click.echo(click.style(
                        '[Error] No name provided in object metadata', fg='red'), err=True)
                    exit(1)

                for container in doc['spec']['template']['spec']['containers']:
                    if container['resources']:
                        _request = container.get(
                            'resources', None).get('requests', None)
                        if _request != None:
                            deployment.resources_requests = container['resources'].get(
                                'requests', None)
                        else:
                            click.echo(click.style(
                                ('[Warning] Module {} resource request provided. This can result '
                                 'in suboptimal deployment placement.').format(_name), fg='yellow'))
                        deployment.resources_requests = container['resources'].get(
                            'requests', None)
                        deployment.resources_limits = container['resources'].get(
                            'limits', None)
                    else:
                        click.echo(click.style(
                            ('[Warning] Module {} resource request provided. This can result '
                             'in suboptimal deployment placement.').format(_name), fg='yellow'))

                self._app_modules.append(deployment)
