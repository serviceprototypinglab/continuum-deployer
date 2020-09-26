import copy
import yaml
import json
import click
import tempfile
import shutil
import subprocess
from bitmath import KiB, MiB, GiB, TiB, PiB, EiB, kB, MB, GB, TB, PB, EB
from progress.spinner import Spinner

from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.utils.config import Config, Setting, SettingValue
from continuum_deployer.utils.file_handling import FileHandling
from continuum_deployer.utils.exceptions import RequirementsError


class Helm(Importer):

    # TODO add support for plain Pods - requires change in parse()
    K8S_OBJECTS = ['Deployment', 'ReplicaSet',
                   'StatefulSet', 'DaemonSet', 'Jobs', 'CronJob']
    K8S_SCALE_CONTROLLER = ['Deployment', 'ReplicaSet', 'StatefulSet']

    @staticmethod
    def parse_k8s_cpu_value(cpu_value):

        if cpu_value is None:
            return None

        # https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
        # CPU calculation based on: https://medium.com/@betz.mark/understanding-resource-limits-in-kubernetes-cpu-time-9eff74d3161b
        if type(cpu_value) is str and 'm' in cpu_value:
            cpu_value = cpu_value.strip('m')
            cpu_value = int(cpu_value)/1000

        return float(cpu_value)

    @staticmethod
    def parse_k8s_memory_value(memory_value):
        # https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
        # https://medium.com/@betz.mark/understanding-resource-limits-in-kubernetes-memory-6b41e9a955f9
        _K8S_MEMORY_SUFFIXES_FIXED = ['E', 'P', 'T', 'G', 'M', 'K']
        _K8S_MEMORY_SUFFIXES_POWER = ['Ei', 'Pi', 'Ti', 'Gi', 'Mi', 'Ki']
        _K8S_MEMORY_SUFFIXES = \
            ['e'], _K8S_MEMORY_SUFFIXES_FIXED, _K8S_MEMORY_SUFFIXES_POWER

        if type(memory_value) is str:
            # exponential notation e.g. 3e2 = 300
            if 'e' in memory_value:
                memory_value = float(memory_value)
            # check if power-of-two notation is used
            # it is important to check power-of-two first as fixed-point comparison would also match
            elif [e for e in _K8S_MEMORY_SUFFIXES_POWER if(e in memory_value)]:
                if 'Ki' in memory_value:
                    memory_value = memory_value.strip('Ki')
                    memory_value = KiB(float(memory_value)).to_MB().value
                elif 'Mi' in memory_value:
                    memory_value = memory_value.strip('Mi')
                    memory_value = MiB(float(memory_value)).to_MB().value
                elif 'Gi' in memory_value:
                    memory_value = memory_value.strip('Gi')
                    memory_value = GiB(float(memory_value)).to_MB().value
                elif 'Ti' in memory_value:
                    memory_value = memory_value.strip('Ti')
                    memory_value = TiB(float(memory_value)).to_MB().value
                elif 'Pi' in memory_value:
                    memory_value = memory_value.strip('Ki')
                    memory_value = PiB(float(memory_value)).to_MB().value
                elif 'Ei' in memory_value:
                    memory_value = memory_value.strip('Ei')
                    memory_value = EiB(float(memory_value)).to_MB().value
                else:
                    raise NotImplementedError(
                        'Memory value unit of {} not implemented'.format(memory_value))
            # check if fixed-point integer notation is used
            elif [e for e in _K8S_MEMORY_SUFFIXES_FIXED if(e in memory_value)]:
                if 'M' in memory_value:
                    memory_value = memory_value.strip('M')
                elif 'K' in memory_value:
                    memory_value = memory_value.strip('K')
                    memory_value = kB(float(memory_value)).to_MB().value
                elif 'G' in memory_value:
                    memory_value = memory_value.strip('G')
                    memory_value = GB(float(memory_value)).to_MB().value
                elif 'T' in memory_value:
                    memory_value = memory_value.strip('T')
                    memory_value = TB(float(memory_value)).to_MB().value
                elif 'P' in memory_value:
                    memory_value = memory_value.strip('P')
                    memory_value = PB(float(memory_value)).to_MB().value
                elif 'E' in memory_value:
                    memory_value = memory_value.strip('E')
                    memory_value = EB(float(memory_value)).to_MB().value
                else:
                    raise NotImplementedError(
                        'Memory value unit of {} not implemented'.format(memory_value))
        # direct definition in bytes - convert to MB
        else:
            memory_value = memory_value/float('1e+6')

        return int(memory_value)

    def _check_requirements(self):

        _helm = shutil.which("helm")
        if _helm is None:
            # helm is not available in $PATH
            raise RequirementsError("Helm executable not available in $PATH")

    def _gen_config(self):
        return Config([
            Setting('chart_origin', [
                SettingValue(
                    'archive', description='Takes a local helm chart archive as input'),
                SettingValue(
                    'yaml', 'Reads an already templated YAML file', default=True),
            ])
        ])

    def template_chart_archive(self, archive_path):

        _helm = shutil.which("helm")
        if _helm == '':
            # handle helm not installed
            pass
        _command = [
            _helm,
            'template',
            archive_path
        ]
        _templated_yaml = subprocess.run(
            _command, capture_output=True, text=True)

        return _templated_yaml.stdout

    def get_dsl_content(self, dsl_path):

        _chart_origin = self.config.get_setting(
            'chart_origin').get_value().value
        if _chart_origin == 'yaml':
            return FileHandling.get_file_content(dsl_path)
        elif _chart_origin == 'archive':
            return self.template_chart_archive(dsl_path)
        else:
            raise NotImplementedError

    def parse(self, dsl_input):

        # see default loader deprecation
        # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
        docs = yaml.load_all(dsl_input, Loader=yaml.SafeLoader)

        spinner = Spinner('Parsing DSL ')

        for doc in docs:

            spinner.next()

            if doc is None:
                continue
            if doc['kind'] in self.K8S_OBJECTS:

                # TODO Do we need support for DaemonSets?
                deployment = DeploymentEntity()
                # save YAML doc representation
                deployment.yaml = doc
                _name = doc.get('metadata', None).get('name', None)
                if _name != None:
                    deployment.name = _name
                else:
                    # https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
                    click.echo(click.style(
                        '[Error] No name provided in object metadata', fg='red'), err=True)
                    exit(1)

                _labels = doc['spec']['template']['spec'].get(
                    'nodeSelector', None)
                if _labels is not None:
                    deployment.labels = _labels

                for container in doc['spec']['template']['spec']['containers']:
                    if 'resources' in container:
                        if container['resources'] is not None:
                            _request = container.get(
                                'resources', None).get('requests', None)
                            if _request != None:
                                deployment.memory = Helm.parse_k8s_memory_value(
                                    _request.get('memory'))
                                deployment.cpu = Helm.parse_k8s_cpu_value(
                                    _request.get('cpu'))
                            else:
                                click.echo(click.style(
                                    ('\n[Warning] No resource request provided for module {}. This can result '
                                     'in suboptimal deployment placement.').format(_name), fg='yellow'))

                            _limits = container.get(
                                'resources', None).get('limits', None)
                            if _limits != None and _limits != {}:
                                deployment.memory_limit = Helm.parse_k8s_memory_value(
                                    _limits.get('memory'))
                                deployment.cpu_limit = Helm.parse_k8s_cpu_value(
                                    _limits.get('cpu'))
                            else:
                                # as this is not an hard error just pass
                                pass
                    else:
                        click.echo(click.style(
                            ('\n[Warning] No resource request provided for module {}. This can result '
                             'in suboptimal deployment placement.').format(_name), fg='yellow'))

                # check if we have a scalable controller
                if doc['kind'] in Helm.K8S_SCALE_CONTROLLER:
                    _number_replicas = doc['spec'].get('replicas', 1)

                    # check if we need to scale higher than 1
                    # case 'is None': empty replicas field in yaml
                    if _number_replicas == 1 or _number_replicas is None:
                        self.app_modules.append(deployment)
                    else:
                        _deployment_name = deployment.name
                        for i in range(_number_replicas):
                            # extent deployment name with replica number
                            deployment.name = '{}-{}'.format(
                                _deployment_name, i)
                            # we need deepcopy to create new objects here in order to call append multiple times
                            self.app_modules.append(copy.deepcopy(deployment))
                else:
                    self.app_modules.append(deployment)
