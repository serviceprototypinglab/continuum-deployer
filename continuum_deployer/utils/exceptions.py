class RequirementsError(Exception):
    """An external requirement of a certain application component
    is not satisfied.
    """

    def __init__(self, message=""):
        self.message = message


class FileTypeNotSupported(Exception):
    """The filetype of the given file is not supported by the
    application module that tries to work with it.
    """

    def __init__(self, message=""):
        self.message = message


class ImporterError(Exception):
    """ImporterError is trough on a group of errors that can
    occur during the Importers import process.
    """

    def __init__(self, message=""):
        self.message = message


class SolverError(Exception):
    """SolverError is trough on a group of errors that can
    occur during the solvers matchmaking process.
    """

    def __init__(self, message=""):
        self.message = message
