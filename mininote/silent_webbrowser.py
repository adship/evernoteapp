import os
import webbrowser
from multiprocessing import Process


STDOUT = 1
STDERR = 2

class SilentWebbrowser(Process):
    """
    Process to launch a browser. 

    Stdio streams are suppressed. This is done in a separate process to avoid 
    interferring with the parent process.
    """

    def __init__(self, url):
        """
        :param str url: The url to open in the browser
        """
        super(SilentWebbrowser, self).__init__()
        self.url = url

    def run(self):
        # reference:
        # http://stackoverflow.com/a/2323563
        stdout = os.dup(STDOUT)
        stderr = os.dup(STDERR)
        os.close(STDOUT)
        os.close(STDERR)
        os.open(os.devnull, os.O_RDWR)

        webbrowser.open(self.url)
