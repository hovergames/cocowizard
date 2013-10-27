# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..utils.config import root_dir
from ..utils.log import info, indent

def run():
    controller_dir = (root_dir() / "cocowizard/controller").realpath()

    not_init_py = lambda x: "__init__.py" not in x
    strip_controller_dir = lambda x: x.replace(controller_dir, "")
    strip_extension = lambda x: ".".join(x.split(".")[:-1])
    strip_leading_slash = lambda x: x.lstrip("/")

    files = controller_dir.glob("*.py")
    files = filter(not_init_py, files)
    files = map(strip_controller_dir, files)
    files = map(strip_extension, files)
    files = map(strip_leading_slash, files)
    files = sorted(files)

    info("Controllers available:")
    with indent(steps=4):
        map(info, files)
