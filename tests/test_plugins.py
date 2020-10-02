import os
import pytest

from continuum_deployer.solving.solver import Solver
from continuum_deployer.utils.plugin_loader import PluginLoader


def test_plugin_load_type_solver():
    # Do not load default path for repeatable test results
    pl = PluginLoader(add_default_path=False)
    _file_name = os.path.basename(__file__)
    _test_plugin_path = os.path.realpath(__file__).split('/'+_file_name)
    pl.add_plugins_path('{}/plugins'.format(_test_plugin_path[0]))
    pl.load_plugins()

    for plugin in pl.plugin_manager.getPluginsOfCategory("Solver"):
        # check if plugins are instantiable
        _solver = plugin.plugin_object(None, None)
        assert issubclass(plugin.plugin_object, Solver)
        assert plugin.description == 'This is a demo solver'
        assert plugin.name == 'Demo Solver'
