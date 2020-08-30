from progress.bar import Bar


class UI():

    @staticmethod
    def printPercentBar(prefix: str, percent: int):
        with Bar(prefix, max=100, suffix='%(percent)d%%') as bar:
            bar.next(percent)
