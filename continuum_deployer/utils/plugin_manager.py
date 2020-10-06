from yapsy.PluginManager import PluginManager


class CDPluginManager(PluginManager):

    def instanciateElement(self, element):
        # overwrite necessary cause standard Yaspsy instantiates plugins on load
        # this is not possible in our case as plugins need additional parameters first
        # see also: https://sourceforge.net/p/yapsy/support-requests/8/
        return element
