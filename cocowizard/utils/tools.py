# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh

from . import config

TOOLS_DIR = config.root_dir() / "cocowizard/tools"

xcode_add_source = sh.Command(TOOLS_DIR / "addSourceFile.rb")
