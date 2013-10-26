# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import traceback
from colorama import Fore, Back, Style

def run():
    try:
        controller = sys.argv[1]
        del sys.argv[1]
        sys.argv[0] += " " + controller
        module = __import__("cocowizard.controller.%s" % controller, fromlist=["cocowizard.controller"])
        module.run()
    except IndexError as e:
        error("No controller name given", exit=False)
        debug(e)
    except ImportError as e:
        error("Invalid controller name given", exit=False)
        debug(e)

def error(message, exit=True):
    print(Fore.RED + "[ERROR]", message, Style.RESET_ALL)
    if exit:
        sys.exit()

def warning(message):
    print(Fore.YELLOW + "[WARN]", message, Style.RESET_ALL)

def info(message):
    print("[INFO]", message)

def debug(message):
    if "DEBUG" not in os.environ:
        return

    if isinstance(message, BaseException):
        print(Back.RED + Fore.BLACK + "[EXCEPTION]", message, Style.RESET_ALL)
        traceback.print_exc()
    else:
        print(Fore.GREEN + "[DEBUG] ", message, Style.RESET_ALL)
