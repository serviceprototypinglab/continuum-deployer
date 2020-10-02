from continuum_deployer.utils.plugin_loader import PluginLoader

app_version = "v0.11.0-dev0"

global plugins


def init_plugins():
    global plugins
    pm = PluginLoader()
    pm.load_plugins()
    plugins = pm.get_plugin_manager()


init_plugins()
