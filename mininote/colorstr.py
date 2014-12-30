from colorama import Fore, Style
from sys import stdout


COLORS = {
    'RED': [Fore.RED, Fore.WHITE],
    'BLUE': [Fore.BLUE, Fore.WHITE],
    'GREEN': [Fore.GREEN, Fore.WHITE],
    'DIM': [Style.DIM, Style.NORMAL]
}

def colorstr(style, string):
    """
    Add color commands to the string.

    :param string: The string to color
    :param style: The color or style to apply
    :returns: New string
    """
    if stdout.isatty():
        codes = COLORS[style]
    else:
        codes = ('', '')
    return codes[0] + str(string) + codes[1]
