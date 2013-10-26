# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from sh import git

from ..utils import config
from ..utils.log import info, warning, debug

AVALON_URL = "git@github.com:hovergames/avalon.git"
DYNAMIC_LOCAL_SRC_FILES = """LOCAL_SRC_FILES := hellocpp/main.cpp \\
    $(subst $(LOCAL_PATH)/,,$(wildcard $(LOCAL_PATH)/../../Classes/*.cpp)) \\
    $(subst $(LOCAL_PATH)/,,$(wildcard $(LOCAL_PATH)/../../Classes/*/*.cpp)) \\
    $(subst $(LOCAL_PATH)/,,$(wildcard $(LOCAL_PATH)/../../Classes/*/*/*.cpp)) """
LOCAL_CFLAGS = """# enable c++11 support but "remove" the override specifier with a simple
# preprocessor define - it's not supported yet :(
LOCAL_CFLAGS += -std=c++11 -Doverride=
"""

def run():
    _ensure_installed()
    _configure_android()
    _configure_ios()

def _ensure_installed():
    vendors_dir = path("Vendors").realpath()
    vendors_dir.mkdir_p()

    avalon_dir = vendors_dir / "avalon"
    avalon_git_dir = avalon_dir / ".git"

    if not avalon_dir.exists():
        _add_git_submodule(avalon_dir)
    elif not avalon_git_dir.exists():
        warning("Avalon vendor folder exists but it's NOT managed with git!")
    elif avalon_git_dir.isdir():
        warning("Avalon vendor folder it's NOT a git submodule!")

def _add_git_submodule(avalon_dir):
    info("Adding avalon with all submodules -- this can take a while")
    warning("Do not interrupt this process!")

    debug("Add avalon as submodule")
    for chunk in git("submodule", "add", AVALON_URL, avalon_dir, _iter=True):
        info(chunk, end="")

    debug("Initialize submodules inside of avalon")
    for chunk in git("submodule", "update", "--init", "--recursive", _iter=True, _cwd=avalon_dir):
        info(chunk, end="")

def _configure_android():
    for flavor in ["samsung", "google", "amazon"]:
        base_dir = path("proj.android." + flavor)
        _ensure_local_properties(base_dir, flavor)
        _update_android_mk(base_dir, flavor)
        _update_application_mk(base_dir, flavor)
        _copy_java_files(base_dir, flavor)

def _ensure_local_properties(base_dir, flavor):
    local = base_dir / "local.properties"
    cocos = base_dir / "../../../cocos/2d/platform/android/java/local.properties"
    text = "sdk.dir=%s\n" % config.get("general.android.sdk_dir")

    for dst in [local, cocos]:
        dst = dst.realpath()
        debug("write sdk.dir: " + dst)
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
            while not text[-1]:
                del text[-1]
            text.append("LOCAL_WHOLE_STATIC_LIBRARIES += avalon_static")
            text.append("")
            text.append(LOCAL_CFLAGS)
            text.append(_avalon_features(flavor))
            text.append(_avalon_flavor(flavor))
            text.append("")
            text.append(line)
        else:
            text.append(line)

    # remove empty line at the file end ...
    if not text[-1]:
        del text[-1]

    # ... and add it back again after the avalon import
    text.append("$(call import-module,projects/%s/Vendors/avalon)" % config.get("general.project"))
    text.append("")

    debug("configure: " + mk_file)
    mk_file.write_text("\n".join(text))

def _avalon_features(flavor):
    defines_string = "\n".join(_get_android_defines(flavor))
    features = []

    if "AVALON_CONFIG_ADS_" in defines_string:
        features.append("ads")

    if "AVALON_CONFIG_GAMECENTER_" in defines_string:
        features.append("gamecenter")

    if "AVALON_CONFIG_PAYMENT_ENABLED" in defines_string:
        features.append("payment")

    return "AVALON_FEATURES := %s" % " ".join(features)

def _avalon_flavor(flavor):
    return "AVALON_PLATFORM_FLAVOR := %s" % flavor

def _update_application_mk(base_dir, flavor):
    mk_file = base_dir / "jni" / "Application.mk"
    text = mk_file.text()

    text = text.replace("-DCOCOS2D_DEBUG=1", "-DCOCOS2D_DEBUG=0")
    text += "APP_CPPFLAGS += -O3\n"
    text += "APP_CPPFLAGS += -DNDEBUG\n"
    for define in _get_android_defines(flavor):
        text += "APP_CPPFLAGS += -D%s=1\n" % define
    text += "APP_OPTIM := release\n"

    debug("configure: " + mk_file)
    mk_file.write_text(text)

def _get_android_defines(flavor):
    defines = config.get("libraries.avalon.android." + flavor)
    if isinstance(defines, list):
        return defines
    else:
        return []

def _copy_java_files(base_dir, flavor):
    pass

def _configure_ios():
    pass
