import os
import subprocess
import tempfile


class TextEditorError(Exception):
    """Error editing text"""

class TextEditor(object):
    """Edit a string in a system text editor"""

    def __init__(self, text_editor):
        """
        :param str text_editor: The text editor binary to use
        """
        self.path = None
        self.text_editor = text_editor

    def edit(self, content):
        """
        Open editor to edit content.

        :param str content: The initial text in the editor
        :returns: Updated content
        :raises: TextEditorError
        """
        if not self.path:
            self.path = TextEditor._create_tmpfile(content)

        rcode = subprocess.call('"{}" {}'.format(self.text_editor, self.path), shell=True, cwd=os.path.dirname(self.path))
        if rcode == 127:
            self.cleanup()
            raise TextEditorError('Unable to open text editor')

        with open(self.path) as f:
            self.content = f.read()

        return self.content

    def cleanup(self):
        """Erase tmp file on filesystem"""
        if self.path:
            os.remove(self.path)

    @staticmethod
    def _create_tmpfile(content):
        """
        Create a temp file.

        :param str content: The initial text in the editor
        :returns: Path to file
        """
        fd, path = tempfile.mkstemp(suffix='.txt', prefix='mininote-')
        os.write(fd, content)
        os.close(fd)
        return path
