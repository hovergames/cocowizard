# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh
from path import path

from . import config

monkeywizard = sh.Command(path(config.get("tools.monkeywizard")).expand())
