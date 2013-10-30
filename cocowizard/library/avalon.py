# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from sh import git, cp
from functools import partial

from ..utils import config
from ..utils.log import info, warning, debug, indent
from ..utils.tools import xcode_add_source, xcode_add_system_frameworks, xcode_build_settings

AVALON_URL = "git@github.com:hovergames/avalon.git"
AVALON_REF = "master"

def run():
    _ensure_installed()
    _android_configure()

    if config.has("libraries.avalon.ios"):
        debug("ios")
        with indent():
            _ios_configure()

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

    git_url = config.get("libraries.avalon.git.url", AVALON_URL)
    git_ref = config.get("libraries.avalon.git.ref", AVALON_REF)

    debug("Add avalon as submodule")
    for chunk in git("submodule", "add", git_url, avalon_dir, _iter=True):
        info(chunk, end="")

    debug("Switch avalon to the right branch")
    for chunk in git("checkout", git_ref, _iter=True, _cwd=avalon_dir):
        info(chunk, end="")

    debug("Initialize submodules inside of avalon")
    for chunk in git("submodule", "update", "--init", "--recursive", _iter=True, _cwd=avalon_dir):
        info(chunk, end="")

def _android_configure():
    for flavor in _get_android_targets():
        debug("android.%s" % flavor)
        with indent():
            base_dir = path("proj.android.%s" % flavor)
            _android_update_android_mk(base_dir, flavor)
            _android_update_application_mk(base_dir, flavor)
            _android_copy_java_files(base_dir, flavor)

def _android_update_android_mk(base_dir, flavor):
    mk_file = base_dir / "jni" / "Android.mk"
    text = []

    for line in mk_file.text().split("\n"):
        if "BUILD_SHARED_LIBRARY" in line:
            text.append("LOCAL_WHOLE_STATIC_LIBRARIES += avalon_static")
            text.append("AVALON_PLATFORM_FLAVOR := %s" % flavor)
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

    debug("Configure: %s" % mk_file)
    mk_file.write_text("\n".join(text))

def _android_update_application_mk(base_dir, flavor):
    mk_file = base_dir / "jni" / "Application.mk"

    text = mk_file.text()
    for define in _get_defines("android.%s" % flavor):
        text += "APP_CPPFLAGS += -D%s=1\n" % define

    debug("Configure: %s" % mk_file)
    mk_file.write_text(text)

def _android_copy_java_files(base_dir, flavor):
    android_dir = base_dir.parent.realpath() / "Vendors/avalon/avalon/platform/android"
    flavor_dir = android_dir.parent.realpath() / "android-%s" % flavor
    to_dir = base_dir.realpath()
    force_amazon_gamecenter = _is_google_with_amazon_gamecenter(flavor)

    for feature in _get_avalon_features("android.%s" % flavor):
        for from_dir in [android_dir, flavor_dir]:
            from_dir = path(from_dir) / "_java" / feature
            if feature == "gamecenter" and force_amazon_gamecenter:
                debug("Forcing amazon gamecenter on google")
                from_dir = path(from_dir.replace("-google", "-amazon"))

            if from_dir.exists():
                for subdir in from_dir.glob("*"):
                    debug("Copy Java files: %s" % subdir)
                    cp("-rf", subdir, to_dir)

def _ios_configure():
    pbxproj = path("proj.ios_mac/%s.xcodeproj/project.pbxproj" % config.get("general.project")).realpath()
    if not pbxproj.exists():
        error("pbxproject file not found -- iOS project present?")

    _ios_add_avalon_files(pbxproj)
    _ios_add_apple_frameworks(pbxproj)
    _ios_add_avalon_defines()
    xcode_build_settings(pbxproj, "add", "HEADER_SEARCH_PATHS", "$(SRCROOT)/../Vendors/avalon")

def _ios_add_apple_frameworks(pbxproj):
    debug("Enable Apple frameworks")
    features = _get_avalon_features("ios")

    frameworks = dict()
    def require(x):
        frameworks[x] = True
    def optional(x):
        if x not in frameworks:
            frameworks[x] = False

    if "ads/provider/chartboost" in features:
        optional("AdSupport")
        require("StoreKit")
        require("SystemConfiguration")
        require("QuartzCore")
        require("GameKit")
    if "ads/provider/revmob" in features:
        optional("AdSupport")
        require("StoreKit")
        require("SystemConfiguration")
    if "ads/provider/iad" in features:
        require("iAd")
    if "payment" in features:
        require("StoreKit")
    if "appirater" in features:
        require("CFNetwork")
        require("StoreKit")
        require("SystemConfiguration")
    if "gamecenter" in features:
        require("GameKit")

    if len(frameworks) > 0:
        lines = ["%s.framework %d" % (x, y) for x, y in frameworks.items()]
        xcode_add_system_frameworks(pbxproj, _in="\n".join(lines))

def _ios_add_avalon_defines():
    defines = _get_defines("ios")
    defines = map(lambda x: "#define %s" % x, defines)

    for target in ["ios", "mac"]:
        prefix_file = path("proj.ios_mac/%s/Prefix.pch" % target).realpath()
        if not prefix_file.exists():
            error("Prefix.pch for target %s not found" % target)

        text = prefix_file.text().split("\n")
        text = filter(lambda x: "AVALON_" not in x, text)
        text.extend(defines)

        debug("Configure: %s" % prefix_file)
        prefix_file.write_text("\n".join(text))

def _ios_add_avalon_files(pbxproj):
    features = _get_avalon_features("ios")
    def disabled_features(path):
        if "avalon/platform/ios/" not in path:
            return True

        lower_path = path.lower()
        for check in features:
            if check in lower_path:
                return True

        return False

    files = _ios_get_avalon_files()
    files = filter(disabled_features, files)
    files = "\n".join(files)

    debug("Add all found files to the XCode project")
    xcode_add_source(pbxproj, _in=files)

def _ios_get_avalon_files():
    def platform_ios_only(path):
        if "avalon/avalon/platform/" not in path:
            return True
        if "avalon/avalon/platform/ios/" in path:
            return True
        return False

    def trimsplit(haystack, path):
        parts = path.split(haystack)
        if len(parts) > 1:
            return parts[0] + haystack
        else:
            return path

    hidden_files = lambda x: not x.split("/")[-1].startswith(".")
    trim_lproj = partial(trimsplit, ".lproj/")
    trim_bundle = partial(trimsplit, ".bundle/")
    trim_framework = partial(trimsplit, ".framework/")

    folder = path("Vendors/avalon/avalon")
    if not folder.exists():
        error("Unable to iterate over %s" % folder)

    debug("Search for all files in %s" % folder)
    files = folder.walkfiles()
    files = filter(platform_ios_only, files)
    files = filter(hidden_files, files)
    files = map(trim_lproj, files)
    files = map(trim_bundle, files)
    files = map(trim_framework, files)
    files = set(files)
    files = sorted(files)
    return files

def _get_avalon_features(flavor):
    features = ["ui", "utils"]

    for define in _get_defines(flavor):
        if "_ENABLED" not in define:
            continue

        define = define.lower() \
            .replace("avalon_config_", "") \
            .replace("_enabled", "") \
            .replace("_", "/")
        features.append(define)

    return features

def _is_google_with_amazon_gamecenter(flavor):
    if flavor != "google":
        return False

    defines = " ".join(_get_defines("android.%s" % flavor))
    if "AVALON_CONFIG_GAMECENTER_USE_AMAZON_ON_GOOGLE" not in defines:
        return False

    if "AVALON_CONFIG_GAMECENTER_ENABLED" not in defines:
        return False

    return True

def _get_android_targets():
    key = "libraries.avalon.android"
    if config.has(key):
        return config.get(key).keys()
    else:
        return []

def _get_defines(target):
    defines = config.get("libraries.avalon.%s" % target)
    if isinstance(defines, list):
        return defines
    else:
        return []
