import yaml
import json

from continuum_deployer.extractors.extractor import Extractor
from continuum_deployer.deployment import Deployment


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
                deployment = Deployment()
                deployment.name = doc['metadata']['name']

                for container in doc['spec']['template']['spec']['containers']:
                    if container['resources']:
                        deployment.resources_requests = container['resources'].get(
                            'requests', None)
                        deployment.resources_limits = container['resources'].get(
                            'limits', None)

                self._app_modules.append(deployment)
