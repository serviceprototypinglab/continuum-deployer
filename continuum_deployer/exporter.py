import yaml


class Exporter():
    """Exports a set of matched resources to a deployable YAML"""

    def __init__(self, stdout=False, output_stream=None):
        self.stdout = stdout
        self.output_stream = output_stream

    def _output(self, content):
        """Helper method that exports content to different output targets

        Args:
            content (str): String to output
        """
        if self.stdout:
            print('---')
            print(content)

        if self.output_stream is not None:
            self.output_stream.write('---\n')
            self.output_stream.write(content)

    @staticmethod
    def _add_hostname_label(hostname, deployment):
        """Adds Kubernetes hostname label to deployments

        Args:
            hostname (str): node hostname, label content
            deployment (Deployment): Deployment to add the label to

        Returns:
            Deployment: Deployment object with the added label
        """
        KUBE_HOSTNAME_LABEL_KEY = 'kubernetes.io/hostname'
        result = deployment.yaml
        result.get('spec').get('template').get('spec')['nodeSelector'] = {
            KUBE_HOSTNAME_LABEL_KEY: hostname}
        deployment.yaml = result
        return deployment

    def export(self, matched_resources):
        """Exports a set of matched resources

        Args:
            matched_resources (Resources): Array of matched resources to extract
        """
        for resource in matched_resources:
            for deployment in resource.get_deployments():
                deployment = Exporter._add_hostname_label(
                    resource.name, deployment)
                self._output(yaml.dump(deployment.yaml))
