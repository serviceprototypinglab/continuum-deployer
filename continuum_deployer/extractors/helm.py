import yaml
import json
import click

from continuum_deployer.extractors.extractor import Extractor
from continuum_deployer.deployment import DeploymentEntity


class Helm(Extractor):

    # TODO add support for plain Pods - requires change in parse()
    K8S_OBJECTS = ['Deployment', 'ReplicaSet',
                   'StatefulSet', 'DaemonSet', 'Jobs', 'CronJob']

    @staticmethod
    def parse_k8s_cpu_value(cpu_value):

        if cpu_value is None:
            return None

        # https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
        # CPU calculation based on: https://medium.com/@betz.mark/understanding-resource-limits-in-kubernetes-cpu-time-9eff74d3161b
        if type(cpu_value) is str:
            if 'm' in cpu_value:
                cpu_value = cpu_value.strip('m')
                cpu_value = int(cpu_value)/1000

        return float(cpu_value)

    @staticmethod
    def parse_k8s_memory_value(memory_value):
        # https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
        _K8S_MEMORY_SUFFIXES_FIXED = ['E', 'P', 'T', 'G', 'M', 'K']
        _K8S_MEMORY_SUFFIXES_POWER = ['Ei', 'Pi', 'Ti', 'Gi', 'Mi', 'Ki']
        _K8S_MEMORY_SUFFIXES = \
            ['e'], _K8S_MEMORY_SUFFIXES_FIXED, _K8S_MEMORY_SUFFIXES_POWER

        if type(memory_value) is str:
            # exponential notation e.g. 3e2 = 300
            if 'e' in memory_value:
                memory_value = float(memory_value)
            # check if power-of-two notiation is used
            # it is important to check power-of-two first as fixed-point comparison would also match
            elif [e for e in _K8S_MEMORY_SUFFIXES_POWER if(e in memory_value)]:
                raise NotImplementedError
            # check if fixed-point integer notiation is used
            elif [e for e in _K8S_MEMORY_SUFFIXES_FIXED if(e in memory_value)]:
                if 'M' in memory_value:
                    memory_value = memory_value.strip('M')
                else:
                    raise NotImplementedError
        # direct definition in bytes - convert to MB
        else:
            memory_value = memory_value/float('1e+6')

        return int(memory_value)

    def parse(self, dsl_input):

        # see default loader deprication
        # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
        docs = yaml.load_all(dsl_input, Loader=yaml.SafeLoader)

        for doc in docs:
            if doc['kind'] in self.K8S_OBJECTS:

                # TODO add support for >1 scaled deployments
                deployment = DeploymentEntity()
                # save YAML doc repesentation
                deployment.yaml = doc
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
                            deployment.memory = Helm.parse_k8s_memory_value(
                                _request.get('memory'))
                            deployment.cpu = Helm.parse_k8s_cpu_value(
                                _request.get('cpu'))
                        else:
                            click.echo(click.style(
                                ('[Warning] Module {} resource request provided. This can result '
                                 'in suboptimal deployment placement.').format(_name), fg='yellow'))

                        _limits = container.get(
                            'resources', None).get('limits', None)
                        if _limits != None:
                            deployment.memory_limit = Helm.parse_k8s_memory_value(
                                _limits.get('memory'))
                            deployment.cpu_limit = Helm.parse_k8s_cpu_value(
                                _limits.get('cpu'))
                        else:
                            # as this is not an hard error just pass
                            pass
                    else:
                        click.echo(click.style(
                            ('[Warning] Module {} resource request provided. This can result '
                             'in suboptimal deployment placement.').format(_name), fg='yellow'))

                self.app_modules.append(deployment)
