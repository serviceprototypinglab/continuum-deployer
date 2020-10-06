import os

from continuum_deployer.utils.plugin_manager import CDPluginManager
from continuum_deployer.solving.solver import Solver
from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.dsl.exporter.exporter import Exporter


class PluginLoader:

    def __init__(self, add_default_path=True):

        self.plugins_paths = []

        # add default plugins path
        if add_default_path:
            _cp_module_path = os.path.realpath(__file__).split('/utils')
            self.add_plugins_path('{}/plugins'.format(_cp_module_path[0]))

        # Build the manager
        self.plugin_manager = CDPluginManager()
        # Tell it the default place(s) where to find plugins
        self.plugin_manager.setPluginPlaces(self.plugins_paths)
        # Define the various categories corresponding to the different
        # kinds of plugins you have defined
        self.plugin_manager.setCategoriesFilter({
            "Solver": Solver,
            "Importer": Importer,
            "Exporter": Exporter
        })

    def add_plugins_path(self, path):
        """Adds an additional path to the loader where plugins
        might be placed. A reload is not done automatically.

        :param path: filesystem path where the loader should search for plugins
        :type path: str
        """
        self.plugins_paths.append(path)

    def get_plugin_manager(self):
        """Getter for the plugin manager

        :return: the current instance of the plugin manager
        :rtype: :class:`continuum_deployer.utils.plugin_manager.CDPluginManager`
        """
        return self.plugin_manager

    def load_plugins(self):
        """Triggers the actual plugin loading.
        """
        # Load all plugins
        self.plugin_manager.collectPlugins()
