# pylint: disable=W1401

import click
import pydoc
from progress.bar import Bar


class UI():
    """Helper class that bundels UI related helpers"""

    CLI_BANNER = """
   ____            _   _                               ____             _                       
  / ___|___  _ __ | |_(_)_ __  _   _ _   _ _ __ ___   |  _ \  ___ _ __ | | ___  _   _  ___ _ __ 
 | |   / _ \| '_ \| __| | '_ \| | | | | | | '_ ` _ \  | | | |/ _ \ '_ \| |/ _ \| | | |/ _ \ '__|
 | |__| (_) | | | | |_| | | | | |_| | |_| | | | | | | | |_| |  __/ |_) | | (_) | |_| |  __/ |   
  \____\___/|_| |_|\__|_|_| |_|\__,_|\__,_|_| |_| |_| |____/ \___| .__/|_|\___/ \__, |\___|_|   
                                                                 |_|            |___/           
   {} - Author: Daniel Hass
"""

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

    @staticmethod
    def prompt_std(text):
        return click.prompt(click.style(text, fg='bright_blue'), type=str)

    @staticmethod
    def page(text):
        pydoc.pager(text)
