# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial

from path import path
from sh import git
from yaml import load as yaml_load

from ..utils import config
from ..utils.log import info, warning, debug, indent, error
from ..utils.tools import xcode_add_source, xcode_add_apple_frameworks, xcode_build_settings

UNIQUE_NAMES = set()

def run(check_config=config):
    for name, url, ref in check_config.dependencies():
        dependency_dir = _ensure_installed(name, url, ref)
        dependency_config = config.from_file(dependency_dir / "cocowizard.yml")

        _ios_configure(name, dependency_dir, dependency_config)
        # _android_configure()

        run(dependency_config)

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

def _ios_configure(name, dependency_dir, dependency_config):
    pbxproj = path("proj.ios_mac/%s.xcodeproj/project.pbxproj" % config.get("general.project"))
    if not pbxproj.exists():
        error("pbxproject file not found -- iOS project present?")

    if not dependency_config.get("skip_ios_add_files", False):
        _ios_add_files(pbxproj, dependency_dir)
    xcode_add_apple_frameworks(dependency_config, pbxproj)

    search = "$(SRCROOT)/../Vendors/%s/src/" % name
    xcode_build_settings(pbxproj, "add", "HEADER_SEARCH_PATHS", search)

    _ios_add_define(name)

def _ios_add_files(pbxproj, dependency_dir):
    files = _ios_get_files(dependency_dir)
    if not files:
        return

    debug("Add all found files to the XCode project")
    xcode_add_source(pbxproj, _in="\n".join(files))

def _ios_get_files(dependency_dir):
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

def _ios_add_define(name):
    name = name.upper().replace("-", "_").replace("/", "_")

    global UNIQUE_NAMES
    UNIQUE_NAMES.add(name)

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
