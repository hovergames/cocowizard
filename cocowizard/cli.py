# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from path import path

from .utils.log import debug, error

def run():
    try:
        controller = sys.argv[1]
        del sys.argv[1]
        sys.argv[0] += " " + controller
    except IndexError as e:
        debug(e)
        error("No controller name given. See 'cocowizard help'.")

    try:
        module = __import__("cocowizard.controller.%s" % controller, fromlist=["cocowizard.controller"])
        module.run()
    except ImportError as e:
        debug(e)
        error("Invalid controller name given. See 'cocowizard help'.")
