# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
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
    _configure_ios_name()

    _configure_mac_resulution_and_title()

    _configure_android_name()
    _configure_android_version()
    _configure_android_orientation()

def _get_proj_dir_ios():
    proj_dir = path("proj.ios_mac").realpath()
    if not proj_dir.exists():
        error("No ios project generated yet -- try cocowizard update")
    return proj_dir

def _get_proj_dir_android(flavor):
    proj_dir = path("proj.android.%s" % flavor).realpath()
    if not proj_dir.exists():
        error("No android.%s project generated yet -- try cocowizard update" % flavor)
    return proj_dir

def _configure_ios_name():
    search = "<string>${PRODUCT_NAME}</string>"
    replace = "<string>%s</string>" % config.get("general.app_name")

    plist_file = _get_proj_dir_ios() / PLIST_FILE
    text = plist_file.text()
    text = text.replace(search, replace)
    plist_file.write_text(text)

def _configure_ios_orientation():
    orientation = config.get("general.orientation")
    if orientation == "landscape":
        pass
    elif orientation == "portrait":
        plist_file = _get_proj_dir_ios() / PLIST_FILE
        text = plist_file.text()
        text = text.replace("UIInterfaceOrientationLandscapeRight", "UIInterfaceOrientationPortrait")
        text = text.replace("UIInterfaceOrientationLandscapeLeft", "UIInterfaceOrientationPortraitUpsideDown")
        plist_file.write_text(text)
    else:
        error("Orientation in configuration is invalid.")

def _configure_mac_resulution_and_title():
    cpp_file = _get_proj_dir_ios() / "mac/main.cpp"
    regex = re.compile(r"eglView.init\(.*\)")

    title = config.get("general.mac.title")
    resolution = config.get("general.mac.resolution").split("x")
    template = (title, int(resolution[0]), int(resolution[1]))

    text = cpp_file.text()
    text = regex.sub("eglView.init(\"%s\", %d, %d)" % template, text)
    cpp_file.write_text(text)

def _configure_ios_package_name():
    package = config.get("general.package")
    project = config.get("general.project")

    xcode_file = _get_proj_dir_ios() /  XCODE_FILE
    text = xcode_file.text()
    text = text.replace("%s iOS" % project, project)
    xcode_file.write_text(text)

    plist_file = _get_proj_dir_ios() / PLIST_FILE
    text = plist_file.text()
    text = text.replace("org.cocos2d-x.${PRODUCT_NAME:rfc1034identifier}", package)
    plist_file.write_text(text)

def _configure_android_orientation():
    for flavor in config.android_flavors():
        orientation = config.get("general.orientation")
        if orientation == "landscape":
            pass
        elif orientation == "portrait":
            manifest_file = _get_proj_dir_android(flavor) / "AndroidManifest.xml"
            text = manifest_file.text()
            text = text.replace("landscape", "portrait")
            manifest_file.write_text(text)
        else:
            error("Orientation in configuration is invalid.")

def _configure_ios_version():
    plist_file = _get_proj_dir_ios() / PLIST_FILE
    text = plist_file.text()

    if text.count("<string>1.0</string>") <> 1:
        error("Invalid Info.plist file!")

    text = text.replace("<string>1.0</string>", "<string>%s</string>" % config.get("general.version"))
    plist_file.write_text(text)

def _configure_android_version():
    prefer_amazon = config.get("general.android.prefer_amazon_over_google")

    for flavor in config.android_flavors():
        version_name = str(config.get("general.version"))
        if flavor == "amazon" and prefer_amazon:
            version_name += ".0"
        version_code = version_name.replace(".", "")

        manifest_file = _get_proj_dir_android(flavor) / "AndroidManifest.xml"
        text = manifest_file.text()
        text = text.replace("android:versionCode=\"1\"", "android:versionCode=\"%s\"" % version_code)
        text = text.replace("android:versionName=\"1.0\"", "android:versionName=\"%s\"" % version_name)
        manifest_file.write_text(text)

def _configure_android_name():
    search = '<string name="app_name">%s</string>' % config.get("general.project")
    replace = '<string name="app_name">%s</string>' % config.get("general.app_name")

    for flavor in config.android_flavors():
        string_res = _get_proj_dir_android(flavor) / "res/values/strings.xml"
        text = string_res.text()
        text = text.replace(search, replace)
        string_res.write_text(text)
