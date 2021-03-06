# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
import sh

from ..utils import config
from ..utils.log import error, debug, indent

IOS_SIZES = [29, 40, 50, 57, 58, 72, 76, 80, 100, 114, 120, 144, 152]
ANDROID_SIZES = [[48, "mdpi"], [32, "ldpi"], [72, "hdpi"], [96, "xhdpi"]]

def run():
    debug("ios")
    with indent():
        _configure_ios()
        _configure_launch_images_ios()

    for flavor in config.android_flavors():
        debug("android.%s" % flavor)
        with indent():
            _configure_android(flavor)

def _get_ios_path():
    proj_dir = path("proj.ios_mac/ios")
    if not proj_dir.exists():
        error("No ios project generated yet -- try cocowizard update")
    return proj_dir

def _get_icon_path(target):
    icons_dir = path("Meta/_generated/%s" % target)
    if not icons_dir.exists():
        error("No icons generated yet -- try cocowizard generate_icons")
    return icons_dir

def _configure_ios():
    icons_dir = _get_icon_path("ios")
    proj_dir = _get_ios_path()

    for size in IOS_SIZES:
        icon_from = icons_dir / ("icon-%s.png" % size)
        icon_to = proj_dir / ("Icon-%s.png" % size)

        if not icon_from.exists():
            error("Icon size %s required for iOS. See cocowizard.yml!" % size)

        debug("Copy: %s" % icon_to)
        icon_from.copy(icon_to)

def _configure_launch_images_ios():
    source_dir = path("Meta/launch_images/")
    if not source_dir.exists():
        error("Launch images not generated yet -- try cocowizard generate_icons")

    proj_dir = _get_ios_path()
    images = ["Default.png", "Default-568h@2x.png", "Default@2x.png"]
    for image in images:
        (source_dir / image).copy(proj_dir / image)

def _configure_android(flavor):
    proj_dir = path("proj.android.%s" % flavor)
    if not proj_dir.exists():
        error("No android.%s project generated yet -- try cocowizard update" % flavor)

    icons_dir = _get_icon_path("android.%s" % flavor)
    for size, mode in ANDROID_SIZES:
        icon_from = icons_dir / ("icon-%s.png" % size)
        icon_to = proj_dir / ("res/drawable-%s/icon.png" % mode)

        if not icon_from.exists():
            error("Icon size %s required for android.%s. See cocowizard.yml!" % (size, flavor))

        debug("Copy: %s" % icon_to)
        icon_to.parent.makedirs_p()
        icon_from.copy(icon_to)
