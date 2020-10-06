import yaml

from yapsy.IPlugin import IPlugin


class Exporter(IPlugin):
    """Exports a set of matched resources to a deployable DSL"""

    def __init__(self, stdout=False, output_stream=None):
        self.stdout = stdout
        self.output_stream = output_stream

    def export(self, matched_resources):
        """Exports matched resources to target format

        :param matched_resources: list of resources with matched deployments
        :type matched_resources: list
        """
        raise NotImplementedError
