import yaml

from yapsy.IPlugin import IPlugin


class Exporter(IPlugin):
    """Exports a set of matched resources to a deployable YAML"""

    def __init__(self, stdout=False, output_stream=None):
        self.stdout = stdout
        self.output_stream = output_stream

    def export(self, matched_resources):
        """Exports a set of matched resources

        Args:
            matched_resources (Resources): Array of matched resources to extract
        """
        raise NotImplementedError
