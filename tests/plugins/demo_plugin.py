from yapsy.IPlugin import IPlugin


class DemoPlugin(IPlugin):

    def activate(self):
        print('Demo Plugin activated!')
