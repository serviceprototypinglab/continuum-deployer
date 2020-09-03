import yaml


class Exporter():

    def __init__(self, stdout=False):
        self.stdout = stdout

    def _output(self, content):
        if self.stdout:
            print('---')
            print(content)

    def _add_hostname_label(self, hostname, deployment):
        KUBE_HOSTNAME_LABEL_KEY = 'kubernetes.io/hostname'
        result = deployment.yaml
        result.get('spec').get('template').get('spec')['nodeSelector'] = {
            KUBE_HOSTNAME_LABEL_KEY: hostname}
        deployment.yaml = result
        return deployment

    def export(self, matchedResources):
        for resource in matchedResources:
            for deployment in resource.get_deployments():
                deployment = self._add_hostname_label(
                    resource.name, deployment)
                self._output(yaml.dump(deployment.yaml))
