# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from sh import cp

from ..utils import config
from ..utils.log import debug, indent, error
from ..utils.tools import xcode_add_source

DYNAMIC_LOCAL_SRC_FILES = """LOCAL_SRC_FILES := hellocpp/main.cpp \\
    $(subst $(LOCAL_PATH)/,,$(wildcard $(LOCAL_PATH)/../../Classes/*.cpp)) \\
    $(subst $(LOCAL_PATH)/,,$(wildcard $(LOCAL_PATH)/../../Classes/*/*.cpp)) \\
    $(subst $(LOCAL_PATH)/,,$(wildcard $(LOCAL_PATH)/../../Classes/*/*/*.cpp))"""
LOCAL_CFLAGS = """# enable c++11 support but "remove" the override specifier with a simple
# preprocessor define - it's not supported yet :(
LOCAL_CFLAGS += -std=c++11 -Doverride=
"""

def run():
    _configure_android()

    debug("ios")
    with indent():
        _configure_ios()

def _configure_ios():
    folder = path("Classes")
    if not folder.exists():
        error("Unable to iterate over %s" % folder)

    pbxproj = path("proj.ios_mac/%s.xcodeproj/project.pbxproj" % config.get("general.project")).realpath()
    if not pbxproj.exists():
        error("pbxproject file not found -- iOS project present?")

    debug("Search for all files in %s" % folder)
    queue = folder.walkfiles()

    debug("Add all found files to the XCode project")
    xcode_add_source(pbxproj, _in="\n".join(queue))

def _configure_android():
    for flavor in ["samsung", "google", "amazon"]:
        debug("android.%s" % flavor)
        with indent():
            base_dir = path("proj.android.%s" % flavor)
            _ensure_local_properties(base_dir, flavor)
            _update_android_mk(base_dir, flavor)
            _update_application_mk(base_dir, flavor)

def _ensure_local_properties(base_dir, flavor):
    local = base_dir / "local.properties"
    cocos = base_dir / "../../../cocos/2d/platform/android/java/local.properties"
    text = "sdk.dir=%s\n" % config.get("general.android.sdk_dir")

    for dst in [local, cocos]:
        dst = dst.realpath()
        debug("Write sdk.dir: %s" % dst)
        dst.write_text(text)

def _update_android_mk(base_dir, flavor):
    mk_file = base_dir / "jni" / "Android.mk"
    text = []

    for line in mk_file.text().split("\n"):
        if "LOCAL_SRC_FILES" in line:
            text.append(DYNAMIC_LOCAL_SRC_FILES)
        elif "../../Classes/" in line:
            pass
        elif "BUILD_SHARED_LIBRARY" in line:
            text.append(LOCAL_CFLAGS)
            text.append(line)
        else:
            text.append(line)

    debug("Configure: %s" % mk_file)
    mk_file.write_text("\n".join(text))

def _update_application_mk(base_dir, flavor):
    mk_file = base_dir / "jni" / "Application.mk"
    text = mk_file.text()

    text = text.replace("-DCOCOS2D_DEBUG=1", "-DCOCOS2D_DEBUG=0")
    text += "APP_CPPFLAGS += -O3\n"
    text += "APP_CPPFLAGS += -DNDEBUG\n"
    text += "APP_OPTIM := release\n"

    debug("Configure: %s" % mk_file)
    mk_file.write_text(text)
