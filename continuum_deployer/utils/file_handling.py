class FileHandling:

    @staticmethod
    def get_file_content(path):
        with open(path, "r") as file:
            return file.read()
