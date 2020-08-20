from continuum_deployer.deployment import Deployment

class Extractor:

    _app_modules = []

    def __init__(self):
        pass

    def parse(self, dsl_input):
        raise NotImplementedError

    def get_app_modules(self):
        return self._app_modules

    def print_app_modules(self):
        for module in self._app_modules:
            print(module)