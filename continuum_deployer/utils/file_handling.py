class FileHandling:

    @staticmethod
    def get_file_content(path):
        """Helper function that returns the str content of
        the file at the given path.

        :param path: path to the file to read
        :type path: str
        :return: content of the file as plain str
        :rtype: str
        """
        with open(path, "r") as file:
            return file.read()
