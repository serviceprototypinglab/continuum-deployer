from continuum_deployer.utils.plugin_manager import CDPluginManager

from continuum_deployer.solving.solver import Solver


class PluginLoader:

    PLUGIN_PATH = '/workspaces/continuum-deployer/continuum_deployer/plugins'

    def __init__(self):
        # Build the manager
        self.plugin_manager = CDPluginManager()
        # Tell it the default place(s) where to find plugins
        self.plugin_manager.setPluginPlaces([self.PLUGIN_PATH])
        # Define the various categories corresponding to the different
        # kinds of plugins you have defined
        self.plugin_manager.setCategoriesFilter({
            "Solver": Solver,
        })

    def get_plugin_manager(self):
        return self.plugin_manager

    def load_plugins(self):
        # Load all plugins
        self.plugin_manager.collectPlugins()
