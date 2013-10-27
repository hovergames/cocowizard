# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import traceback
from colorama import Fore, Back, Style
from path import path
from contextlib import contextmanager

CURRENT_DIR = path("./").realpath()
INDENT_LVL = 0
INDENT_STR = ""

def error(message, exit=True, end="\n"):
    _print(Fore.RED + "[ERROR] " + INDENT_STR + message + Style.RESET_ALL, end=end)
    if exit:
        sys.exit()

def warning(message, end="\n"):
    _print(Fore.YELLOW + "[WARN ] " + INDENT_STR + message + Style.RESET_ALL, end=end)

def info(message, end="\n"):
    _print("[INFO ] " + INDENT_STR + message, end=end)

def debug(message, end="\n"):
    if "DEBUG" not in os.environ:
        return

    if isinstance(message, BaseException):
        _print(Back.RED + Fore.BLACK + "[EXCEPTION] " + INDENT_STR + message, Style.RESET_ALL)
        traceback.print_exc()
    else:
        _print(Fore.GREEN + "[DEBUG] " + INDENT_STR + message + Style.RESET_ALL, end=end)

@contextmanager
def indent():
    global INDENT_LVL
    global INDENT_STR

    INDENT_LVL += 2
    INDENT_STR += " " * INDENT_LVL

    yield

    INDENT_LVL -= 2
    INDENT_STR = " " * INDENT_LVL

def _print(message, end):
    print(message.replace(CURRENT_DIR, "."), end=end)
