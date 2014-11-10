import os
import subprocess
import tempfile


EDITOR  = "/usr/bin/vim" # TODO: configurable

class TextEditor:
    """Edit a string in a system text editor"""

    def __init__(self, content):
        """
        :param content: The initial text in the editor
        """
        self.content = content

        fd, path = tempfile.mkstemp(suffix='.txt', prefix='mininote-')
        os.write(fd, self.content)
        os.close(fd)
        self.path = path

    def edit(self):
        """
        Open editor to edit content

        :returns: Updated content
        """
        subprocess.call('{} {}'.format(EDITOR, self.path), shell = True, cwd = os.path.dirname(self.path))

        with open(self.path) as f:
            self.content = f.read()

        return self.content

    def cleanup(self):
        """Erase tmp file on filesystem"""
        os.remove(self.path)
