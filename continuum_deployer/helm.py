import yaml, json

from deployment import Deployment

class Helm:

    K8S_OBJECTS = ['StatefulSet', 'Deployment']
    
    deployments = []
    
    def __init__(self):
        pass

    def parse(self, document):

        # see default loader deprication
        # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
        docs = yaml.load_all(document, Loader=yaml.SafeLoader)

        for doc in docs:
            if doc['kind'] in self.K8S_OBJECTS:

                deployment = Deployment()
                deployment.name =  doc['metadata']['name']

                for container in doc['spec']['template']['spec']['containers']:
                    if container['resources']:
                        deployment.resources_requests = container['resources'].get('requests', None)
                        deployment.resources_limits = container['resources'].get('limits', None)
                
                self.deployments.append(deployment)

    def printDeploymetsJson(self):
        for deployment in self.deployments:
            print(json.dumps(deployment.__dict__))
