import os
import sys


def clear_terminal():
    if sys.platform.startswith('win32'):
        os.system('cls')
    else:
        os.system('clear')

