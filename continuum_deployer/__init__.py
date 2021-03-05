from continuum_deployer.utils.plugin_loader import PluginLoader

app_version = "v1.0.0"

global plugins


def init_plugins():
    global plugins
    pl = PluginLoader()
    pl.load_plugins()
    plugins = pl


init_plugins()
