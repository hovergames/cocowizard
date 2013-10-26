# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh
from path import path

from ..cli import debug
from .recreate_projects import run as recreate_projects

def run():
    debug(">>> recreate_projects")
    recreate_projects()
