class RequirementsError(Exception):

    def __init__(self, message=""):
        self.message = message


class FileTypeNotSupported(Exception):

    def __init__(self, message=""):
        self.message = message
