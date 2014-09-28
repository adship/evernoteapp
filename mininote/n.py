#!/usr/bin/env python
import argparse
import logging
import os
import re
import platform
from mininote import Mininote


logger = logging.getLogger(__name__)

def get_tags(note):
    """
    # gets the tag of the note in the format of
    :param note: in the format of "my note is #tag1 #tag2"
    """
    return re.findall(r"#(\w+)", note)

def get_token():
    # gets the authentication token -- dev_token for now
    # TODO: add support for 'real' token
    windows = "Windows" in platform.system()
    my_environ = os.environ.copy()

    if windows:
        path_default = os.path.join(my_environ["USERPROFILE"], "AppData", "Roaming", "mininote")
    else:
        path_default = os.path.join(my_environ["HOME"], ".mininote")
    logger.info("getting token from default path: {}".format(path_default))

    try:
        file_name = os.path.join(path_default, "EvernoteDevToken.txt")
        theFile = open(file_name, 'rb')
    except:
        logger.error("unable to open token file" + file_name)
        return

    theString = theFile.read()
    return theString.strip()

def get_cmd():
    # user enters the note with tag at command prompt
    return raw_input('mininote>')


if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel('DEBUG')
    root_logger.addHandler(logging.StreamHandler())

    token = get_token()
    if token:
        mn = Mininote(token)
        note = get_cmd()
        mn.add_note(note, get_tags(note))

        
