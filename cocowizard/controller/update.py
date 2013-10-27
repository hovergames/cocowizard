# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh
from path import path

from ..utils import config
from ..utils.log import debug, indent
from .configure_icons import run as configure_icons
from .configure_libraries import run as configure_libraries
from .generate_icons import run as icons
from .recreate_projects import run as recreate_projects

def run():
    config.fail_on_missing_config()

    debug("Run controller: recreate_projects")
    with indent():
        recreate_projects()

    debug("Run controller: configure_libraries")
    with indent():
        configure_libraries()

    debug("Run controller: icons")
    with indent():
        icons()

    debug("Run controller: configure_icons")
    with indent():
        configure_icons()
