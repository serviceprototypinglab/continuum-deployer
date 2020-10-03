class RequirementsError(Exception):

    def __init__(self, message=""):
        self.message = message


class FileTypeNotSupported(Exception):

    def __init__(self, message=""):
        self.message = message


class ImporterError(Exception):

    def __init__(self, message=""):
        self.message = message


class SolverError(Exception):

    def __init__(self, message=""):
        self.message = message
