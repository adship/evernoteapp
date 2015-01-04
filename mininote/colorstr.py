from colorama import Fore, Style
from sys import stdout


COLORS = {
    'RED': (Fore.RED, Fore.RESET),
    'BLUE': (Fore.BLUE, Fore.RESET),
    'GREEN': (Fore.GREEN, Fore.RESET),
    'MAGENTA': (Fore.MAGENTA, Fore.RESET),
    'DIM': (Style.DIM, Style.RESET_ALL),
    'BRIGHT-CYAN': (Fore.CYAN + Style.BRIGHT, Fore.RESET + Style.RESET_ALL)
}

def colorstr(style, string):
    """
    Add color commands to the string.

    :param string: The string to color
    :param style: The style to apply
    :returns: New string
    """
    if stdout.isatty():
        codes = COLORS[style]
    else:
        codes = ('', '')
    return codes[0] + str(string) + codes[1]
