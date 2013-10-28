# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
import sh

from ..utils import config
from ..utils.log import error, debug, indent

XCODE_FILE = config.get("general.project") + ".xcodeproj/project.pbxproj"
PLIST_FILE = "ios/Info.plist"

def run():
    _configure_ios_package_name()
    _configure_ios_version()
    _configure_ios_orientation()

def _get_proj_dir():
    proj_dir = path("proj.ios_mac").realpath()
    if not proj_dir.exists():
        error("No ios project generated yet -- try cocowizard update")
    return proj_dir

def _configure_ios_orientation():
    orientation = config.get("general.orientation")
    if orientation == "landscape":
        pass
    elif orientation == "portrait":
        plist_file = _get_proj_dir() / PLIST_FILE
        text = plist_file.text()
        text = text.replace("UIInterfaceOrientationLandscapeRight", "UIInterfaceOrientationPortrait")
        text = text.replace("UIInterfaceOrientationLandscapeLeft", "UIInterfaceOrientationPortraitUpsideDown")
        plist_file.write_text(text)
    else:
        error("Orientation in configuration is invalid.")

def _configure_ios_package_name():
    project = config.get("general.project")
    package = config.get("general.package")

    xcode_file = _get_proj_dir() /  XCODE_FILE
    text = xcode_file.text()
    text = text.replace("%s iOS" % project, project)
    xcode_file.write_text(text)

    plist_file = _get_proj_dir() / PLIST_FILE
    text = plist_file.text()
    package_prefix = package.replace(project, "")
    text = text.replace("org.cocos2d-x.", package_prefix)
    plist_file.write_text(text)

def _configure_ios_version():
    plist_file = _get_proj_dir() / "ios/Info.plist"
    text = plist_file.text()

    if text.count("<string>1.0</string>") <> 1:
        error("Invalid Info.plist file!")

    text = text.replace("<string>1.0</string>", "<string>%s</string>" % config.get("general.version"))
    plist_file.write_text(text)
