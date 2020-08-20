from continuum_deployer.deployment import Deployment


class Extractor:
    """Interface that defines interaction with several DSL specific extractor implementations."""

    _app_modules = []

    def __init__(self):
        pass

    def parse(self, dsl_input):
        """Handles actual parsing of DSL to internal data structures. Needs to be implemented by child."""
        raise NotImplementedError

    def get_app_modules(self):
        """Getter method for application modules"""
        return self._app_modules

    def print_app_modules(self):
        """Convenience helper that prints object representation of application modules"""
        for module in self._app_modules:
            print(module)
