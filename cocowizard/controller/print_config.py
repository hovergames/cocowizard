# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..utils import config
from ..utils.log import indent, info

def run():
    _pprint(config.from_file("cocowizard.yml"))

def _pprint(config):
    for key, value in config.items():
        if isinstance(value, dict):
            info("%s:" % key)
            with indent():
                _pprint(value)
        else:
            info("%s: %s" % (key, value))
