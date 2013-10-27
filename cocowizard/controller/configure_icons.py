# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from itertools import ifilter, imap
from functools import partial
from path import path
import sh
import shutil

from ..utils import config
from ..utils.log import error, warning

def run():
    _configure_ios()
    for flavor in ["amazon", "google", "samsung"]:
        _configure_android(flavor)

def _configure_ios():
    icons_dir = path("Meta/_generated/ios")
    if not icons_dir.exists():
        error("No ios icons generated yet -- try cocowizard generate_icons")

    proj_dir = path("proj.ios_mac/ios").realpath()
    if not proj_dir.exists():
        error("No ios project generated yet -- try cocowizard update")

    sizes = [29, 40, 50, 57, 58, 72, 76, 80, 100, 114, 120, 144, 152]
    for size in sizes:
        shutil.copy(icons_dir + "/icon-" + str(size) + ".png" , proj_dir + "/Icon-" + str(size) + ".png")

def _configure_android(flavor):
    icons_dir = path("Meta/_generated/android.%s" % flavor)
    if not icons_dir.exists():
        error("No android icons generated yet -- try cocowizard generate_icons")

    proj_dir = path("proj.android.%s" % flavor).realpath()
    if not proj_dir.exists():
        error("No android project generated yet -- try cocowizard update")

    icons = [[48, "mdpi"], [32, "ldpi"], [72, "hdpi"]]
    for icon in icons:        
        shutil.copy(icons_dir + "/icon-" + str(icon[0]) + ".png" , proj_dir + "/res/drawable-" + icon[1] + "/icon.png")
