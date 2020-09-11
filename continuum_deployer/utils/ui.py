from progress.bar import Bar


class UI():
    """Helper class that bundels UI related helpers"""

    @staticmethod
    def print_percent_bar(prefix: str, percent: int):
        """Prints a progress bar to stdout

        Args:
            prefix (str): Label infront of progress bar
            percent (int): Percentage representing the progress
        """
        with Bar(prefix, max=100, suffix='%(percent)d%%') as bar:
            bar.next(percent)

    @staticmethod
    def pretty_label_string(labels):
        """Convert label to string

        Args:
            labels (dict): labels to convert

        Returns:
            str: comma seperated list of labels (key:label,..)
        """
        _result = ""
        if labels is not None:
            for key in labels:
                _result += "{}:{} ".format(key, labels[key])
        return _result.rstrip()
