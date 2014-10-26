class Note:
    def __init__(self, text, updated_time = None):
        """
        :param text: Note string
        :param updated_time: Time in epoc time
        """
        self.text = text
        self.updated_time = updated_time

    def __str__(self):
        return '<Note {}>'.format(self.text)
