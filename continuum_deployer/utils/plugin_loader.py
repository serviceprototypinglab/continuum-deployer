import os

from continuum_deployer.utils.plugin_manager import CDPluginManager
from continuum_deployer.solving.solver import Solver
from continuum_deployer.dsl.importer.importer import Importer


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
        })

    def add_plugins_path(self, path):
        self.plugins_paths.append(path)

    def get_plugin_manager(self):
        return self.plugin_manager

    def load_plugins(self):
        # Load all plugins
        self.plugin_manager.collectPlugins()
