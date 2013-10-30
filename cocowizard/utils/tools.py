# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh

from . import config

TOOLS_DIR = config.root_dir() / "cocowizard/tools"

xcode_add_source = sh.Command(TOOLS_DIR / "xcode_add_source.rb")
xcode_add_system_frameworks = sh.Command(TOOLS_DIR / "xcode_add_system_frameworks.rb")
xcode_build_settings = sh.Command(TOOLS_DIR / "xcode_build_settings.rb")
xcode_clear_classes_and_resources = sh.Command(TOOLS_DIR / "xcode_clear_classes_and_resources.rb")
