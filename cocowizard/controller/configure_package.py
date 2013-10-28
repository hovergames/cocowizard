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

ANDROID_FLAVORS = ["google", "samsung", "amazon"]

def run():
    _configure_ios_package_name()
    _configure_ios_version()
    _configure_ios_orientation()

def _get_proj_dir():
    configure_ios_package_name()
    configure_ios_name()
    configure_ios_version()
    configure_ios_orientation()

    configure_android_name()
    configure_android_version()
    configure_android_orientation()

def get_proj_dir_ios():
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

def get_proj_dir_android(flavor):
    proj_dir = path("proj.android.%s" % flavor).realpath()
    if not proj_dir.exists():
        error("No android.%s project generated yet -- try cocowizard update" % flavor)
    return proj_dir

def configure_ios_name():
    search = "<string>${PRODUCT_NAME}</string>"
    replace = "<string>%s</string>" % config.get("general.app_name")

    plist_file = get_proj_dir_ios() / PLIST_FILE
    text = plist_file.text()
    text = text.replace(search, replace)
    plist_file.write_text(text)

def configure_ios_orientation():
    plist_file = get_proj_dir_ios() / PLIST_FILE

    text = plist_file.text()

def _configure_ios_package_name():
    project = config.get("general.project")
    package = config.get("general.package")

    xcode_file = _get_proj_dir() /  XCODE_FILE
    plist_file.write_text(text)

def configure_android_orientation():
    for flavor in ANDROID_FLAVORS:
        manifest_file = get_proj_dir_android(flavor) / "AndroidManifest.xml"
        text = manifest_file.text()

        orientation = str(config.get("general.orientation"))
        if orientation == "landscape":
            pass
        elif orientation == "portrait":
            text = text.replace("landscape", "portrait")
        else:
            error("Orientation in configuration is invalid.")
        manifest_file.write_text(text)

def configure_ios_package_name():
    project = config.get("general.project")
    package = config.get("general.package")

    xcode_file = get_proj_dir_ios() /  XCODE_FILE
    
    text = xcode_file.text()
    text = text.replace("%s iOS" % project, project)
    xcode_file.write_text(text)

    package_prefix = package.replace(project, "")
    plist_file = get_proj_dir_ios() / PLIST_FILE
    text = plist_file.text()
    text = text.replace("org.cocos2d-x.", package_prefix)
    plist_file.write_text(text)

def _configure_ios_version():
    plist_file = get_proj_dir_ios() / PLIST_FILE
    text = plist_file.text()

    if text.count("<string>1.0</string>") <> 1:
        error("Invalid Info.plist file!")

    text = text.replace("<string>1.0</string>", "<string>%s</string>" % config.get("general.version"))
    plist_file.write_text(text)

def configure_android_version():
    for flavor in ANDROID_FLAVORS:
        manifest_file = get_proj_dir_android(flavor) / "AndroidManifest.xml"
        text = manifest_file.text()

        version_name = str(config.get("general.version"))
        version_code = str(config.get("general.version")).replace(".", "")

        text = text.replace("android:versionCode=\"1\"", "android:versionCode=\"%s\"" % version_code)
        text = text.replace("android:versionName=\"1.0\"", "android:versionName=\"%s\"" % version_name)

        manifest_file.write_text(text)

def configure_android_name():
    search = '<string name="app_name">%s</string>' % config.get("general.project")
    replace = '<string name="app_name">%s</string>' % config.get("general.app_name")

    for flavor in ANDROID_FLAVORS:
        string_res = get_proj_dir_android(flavor) / "res/values/strings.xml"
        text = string_res.text()
        text = text.replace(search, replace)
        string_res.write_text(text)
