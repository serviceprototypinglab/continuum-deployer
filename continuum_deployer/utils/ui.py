from progress.bar import Bar


class UI():

    @staticmethod
    def print_percent_bar(prefix: str, percent: int):
        with Bar(prefix, max=100, suffix='%(percent)d%%') as bar:
            bar.next(percent)

    @staticmethod
    def pretty_label_string(labels):
        _result = ""
        if labels is not None:
            for key in labels:
                _result += "{}:{} ".format(key, labels[key])
        return _result.rstrip()
