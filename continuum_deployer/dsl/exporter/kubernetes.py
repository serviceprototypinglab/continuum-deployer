import yaml

from continuum_deployer.dsl.exporter.exporter import Exporter
from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.resources.resource_entity import ResourceEntity


class Kubernetes(Exporter):

    @staticmethod
    def _add_hostname_label(hostname, deployment: DeploymentEntity):
        """Adds Kubernetes hostname label to deployments

        :param hostname: node hostname, content of added label
        :type hostname: str
        :param deployment: deployment objects to add hostname label to
        :type deployment: :class:`continuum_deployer.resources.deployment.DeploymentEntity`
        :return: deployment object with added labels
        :rtype: :class:`continuum_deployer.resources.deployment.DeploymentEntity`
        """

        KUBE_HOSTNAME_LABEL_KEY = 'kubernetes.io/hostname'
        result = deployment.yaml
        result.get('spec').get('template').get('spec')['nodeSelector'] = {
            KUBE_HOSTNAME_LABEL_KEY: hostname}
        deployment.yaml = result
        return deployment

    def _output(self, content):
        """Helper method that exports content to different output targets

        :param content: content that shall be outputted
        :type content: str
        """

        if self.stdout:
            print('---')
            print(content)

        if self.output_stream is not None:
            self.output_stream.write('---\n')
            self.output_stream.write(content)

    def export(self, matched_resources: ResourceEntity):
        """Exports a set of matched resources

        :param matched_resources: list of matched resources entities to export
        :type matched_resources: :class:`continuum_deployer.resources.resource_entity.ResourceEntity`
        """
        """Exports a set of matched resources

        Args:
            matched_resources (Resources): Array of matched resources to extract
        """
        for resource in matched_resources:
            for deployment in resource.get_deployments():
                deployment = Kubernetes._add_hostname_label(
                    resource.name, deployment)
                self._output(yaml.dump(deployment.yaml))
