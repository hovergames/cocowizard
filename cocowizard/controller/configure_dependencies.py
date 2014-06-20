# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial

from path import path
from sh import git, cp
from yaml import load as yaml_load

from ..utils import config
from ..utils.log import info, warning, debug, indent, error
from ..utils.tools import xcode_add_source, xcode_add_apple_frameworks, xcode_build_settings

UNIQUE_NAMES = set()

def run(check_config=config, depth=0):
    for name, url, ref in check_config.dependencies():
        global UNIQUE_NAMES
        UNIQUE_NAMES.add(name.upper().replace("-", "_").replace("/", "_"))

        dependency_dir = _ensure_installed(name, url, ref)
        dependency_config = config.from_file(dependency_dir / "cocowizard.yml")

        _ios_configure(name, dependency_dir, dependency_config)
        _android_configure(name, dependency_dir, dependency_config)

        run(dependency_config, depth+1)

    if depth == 0:
        _android_configure_last()
        _ios_configure_last()

def _ensure_installed(name, url, ref):
    user, repo = name.split("/")

    vendors_dir = path("Vendors") / user
    vendors_dir.makedirs_p()

    dependency_dir = vendors_dir / repo
    dependency_git_dir = dependency_dir / ".git"

    if not dependency_dir.exists():
        _add_git_submodule(name, url, ref, dependency_dir)
    elif not dependency_git_dir.exists():
        warning("Dependency %s exists but it's NOT managed with git!" % name)
    elif dependency_git_dir.isdir():
        warning("Dependency %s it's NOT a git submodule!" % name)

    return dependency_dir

def _add_git_submodule(name, git_url, git_ref, git_dir):
    info("Downloading %s with all submodules -- this can take a while" % name)
    warning("Do not interrupt this process!")

    debug("Add %s as submodule" % name)
    for chunk in git("submodule", "add", "-f", git_url, git_dir, _iter=True):
        info(chunk, end="")

    debug("Switch %s to the right branch" % name)
    for chunk in git("checkout", git_ref, _iter=True, _cwd=git_dir):
        info(chunk, end="")

    debug("Initialize submodules of %s" % name)
    for chunk in git("submodule", "update", "--init", "--recursive", _iter=True, _cwd=git_dir):
        info(chunk, end="")

def _android_configure(name, dependency_dir, dependency_config):
    def platform_android_only(flavor, path):
        if "platform/" not in path:
        	return True

        p1 = "platform/android/"
        p2 = "platform/android-%s/" % flavor
        if p1 not in path and p2 not in path:
            return False

    if dependency_config.get("android_ignore_java_files", False):
        all_dirs = []
    else:
        all_dirs = dependency_dir.walkdirs()

    if dependency_config.get("android_ignore_src_files", False):
        src_files = []
    else:
        src_files = list((dependency_dir / "src").walkfiles("*.cpp"))

    for flavor in config.android_flavors():
        debug("android.%s" % flavor)
        with indent():
            platform_filter = partial(platform_android_only, flavor)
            flavor_src_files = filter(platform_filter, src_files)
            base_dir = path("proj.android.%s" % flavor)
            _android_update_android_mk(base_dir, flavor, name, flavor_src_files)
            _android_copy_java_files(base_dir, flavor, dependency_dir, all_dirs)

def _android_configure_last():
    for flavor in config.android_flavors():
        debug("android.%s" % flavor)
        with indent():
            base_dir = path("proj.android.%s" % flavor)
            _android_update_application_mk(base_dir, flavor)

def _android_update_android_mk(base_dir, flavor, name, src_files):
    mk_file = base_dir / "jni" / "Android.mk"
    text = mk_file.text()

    add = ["LOCAL_SRC_FILES += ../../%s" % x for x in src_files]
    add.append("LOCAL_C_INCLUDES += ../../Vendors/%s" % name)

    pos = text.find("LOCAL_WHOLE_STATIC_LIBRARIES")
    text = text[:pos] + "\n".join(add) + "\n" + text[pos:]

    debug("Configure: %s" % mk_file)
    mk_file.write_text(text)

def _android_update_application_mk(base_dir, flavor):
    defines = map(lambda x: "APP_CPPFLAGS += -DCOCOWIZARD_%s=1" % x, UNIQUE_NAMES)

    id = _android_flavor_to_id(flavor)
    defines.append("APP_CPPFLAGS += -DCOCOWIZARD_PLATFORM_FLAVOR=%s" % id)

    mk_file = base_dir / "jni" / "Application.mk"
    text = mk_file.text().split("\n")
    text = filter(lambda x: "-DCOCOWIZARD_" not in x, text)
    text.extend(defines)

    debug("Configure: %s" % mk_file)
    mk_file.write_text("\n".join(text))

def _android_flavor_to_id(flavor):
    if flavor == "amazon":
        return 1
    elif flavor == "google":
        return 2
    elif flavor == "samsung":
        return 3
    else:
        raise Error("Unknown android flavor: %s" % flavor)

def _android_copy_java_files(base_dir, flavor, dependency_dir, all_dirs):
    def is_java_dir(dir):
        if dir.endswith("android/_java"):
            return True
        elif dir.endswith("android-%s/_java" % flavor):
            return True
        else:
            return False

    java_dirs = filter(is_java_dir, all_dirs)
    if not java_dirs:
        debug("No java files found")
        return

    for from_dir in java_dirs:
        for subdir in from_dir.glob("*"):
            debug("Copy Java files: %s" % subdir)
            cp("-rf", subdir, base_dir)

def _ios_configure(name, dependency_dir, dependency_config):
    pbxproj = path("proj.ios_mac/%s.xcodeproj/project.pbxproj" % config.get("general.project"))
    if not pbxproj.exists():
        error("pbxproject file not found -- iOS project present?")

    if not dependency_config.get("skip_ios_add_files", False):
        _ios_add_files(pbxproj, dependency_dir)
    xcode_add_apple_frameworks(dependency_config, pbxproj)

    search = "$(SRCROOT)/../Vendors/%s/src/" % name
    xcode_build_settings(pbxproj, "add", "HEADER_SEARCH_PATHS", search)

def _ios_configure_last():
    _ios_add_defines()

def _ios_add_files(pbxproj, dependency_dir):
    files = _ios_get_files(dependency_dir)
    if not files:
        return

    debug("Add all found files to the XCode project")
    xcode_add_source(pbxproj, _in="\n".join(files))

def _ios_get_files(dependency_dir):
    def platform_ios_only(path):
        if "platform/" in path and "platform/ios/" not in path:
            return False
        return True

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

    folder = dependency_dir / "src"
    if not folder.exists():
        return []

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

def _ios_add_defines():
    defines = map(lambda x: "#define COCOWIZARD_%s 1" % x, UNIQUE_NAMES)

    for target in ["ios", "mac"]:
        prefix_file = path("proj.ios_mac/%s/Prefix.pch" % target)
        if not prefix_file.exists():
            error("Prefix.pch for target %s not found" % target)
            continue

        text = prefix_file.text().split("\n")
        text = filter(lambda x: "COCOWIZARD_" not in x, text)
        text.extend(defines)

        debug("Configure: %s" % prefix_file)
        prefix_file.write_text("\n".join(text))
