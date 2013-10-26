# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

from ..cli import info
from ..utils import config

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("echo")
    args = parser.parse_args()

    info(args.echo)
    info(config.get("name"))
