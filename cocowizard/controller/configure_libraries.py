# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

from ..library import github_loader
from ..utils import config
from ..utils.log import debug, error, indent

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", default="all", help="name of the library to configure (default: all)")
    args = parser.parse_args()

    libs = config.get("libraries", [])
    if not libs:
        debug("No library configured yet")
        return

    if isinstance(libs, str):
        libs = [libs]
    if not isinstance(libs, list):
        error("libraries in cocowizard.yml must be a list")

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
        with indent():
            module.run()
    except ImportError as e:
        if "/" in library:
            github_loader.run(library)
        else:
            debug(e)
            error("Unable to load library configurator")
