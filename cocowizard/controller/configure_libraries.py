# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

from ..utils import config
from ..utils.log import debug, error

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", default="all", help="name of the library to configure (default: all)")
    args = parser.parse_args()

    libs = config.get("libraries")
    if args.name == "all":
        for name in libs:
            _configure(name)
    else:
        if args.name not in libs:
            error("Given library (%s) is not configured yet" % args.name)
        else:
            _configure(args.name)

def _configure(library):
    debug("Configure library: %s" % library)
    try:
        module = __import__("cocowizard.library.%s" % library, fromlist=["cocowizard.library"])
        module.run()
    except ImportError as e:
        debug(e)
        error("Unable to load library configurator")

