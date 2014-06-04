# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial

from path import path
from sh import git

from ..utils import config
from ..utils.log import info, warning, debug, indent, error
from ..utils.tools import xcode_add_source, xcode_add_system_frameworks, xcode_build_settings


def run(name):
    name = name.lower()

    library_dir = _ensure_installed(name)
    _fail_on_missing_src_folder(name, library_dir)
    _ios_configure(name, library_dir)
    _process_requirements(library_dir)

def _ios_configure(name, library_dir):
    pbxproj = path("proj.ios_mac/%s.xcodeproj/project.pbxproj" % config.get("general.project")).realpath()
    if not pbxproj.exists():
        error("pbxproject file not found -- iOS project present?")

    _ios_add_files(pbxproj, library_dir)
    _ios_add_apple_frameworks(pbxproj, library_dir)
    xcode_build_settings(pbxproj, "add", "HEADER_SEARCH_PATHS", "$(SRCROOT)/../Vendors/")

def _ios_add_apple_frameworks(pbxproj, library_dir):
    frameworks = library_dir / "cocowizard_apple_frameworks.txt"
    if not frameworks.exists():
        debug("No apple framework dependency file found ...")
        return

    lines = []
    for name in frameworks.lines():
        name = name.strip()
        if "[optional]" in name:
            name = name.replace("[optional]", "").strip()
            optional = True
        else:
            optional = False

        debug("Add apple framework: %s (optional: %s)" % (name, optional))
        lines.append("%s.framework %d" % (name, optional))

    xcode_add_system_frameworks(pbxproj, _in="\n".join(lines))

def _ios_add_files(pbxproj, library_dir):
    files = _ios_get_files(library_dir)
    if not files:
        return

    debug("Add all found files to the XCode project")
    xcode_add_source(pbxproj, _in="\n".join(files))

def _ios_get_files(library_dir):
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

    folder = library_dir / "src"
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

def _ensure_installed(name):
    user, repo = name.split("/")

    vendors_dir = path("Vendors") / user
    vendors_dir.makedirs_p()

    library_dir = vendors_dir / repo
    library_git_dir = library_dir / ".git"

    if not library_dir.exists():
        _add_git_submodule(name, library_dir)
    elif not library_git_dir.exists():
        warning("Library %s exists but it's NOT managed with git!" % name)
    elif library_git_dir.isdir():
        warning("Library %s it's NOT a git submodule!" % name)

    return library_dir

def _process_requirements(library_dir):
    requirements = library_dir / "cocowizard_requirements.txt"
    if not requirements.exists():
        debug("No requirements file found ...")
        return

    for name in requirements.lines():
        name = name.strip()

        debug("Process requirement: %s" % name)
        with indent():
            run(name)

def _fail_on_missing_src_folder(name, library_dir):
    if not (library_dir / "src").isdir():
        error("No src/ folder found in library %s!" % name)

def _add_git_submodule(name, git_dir):
    info("Downloading %s with all submodules -- this can take a while" % name)
    warning("Do not interrupt this process!")

    git_url = "git@github.com:%s.git" % name
    git_url = "/Users/michaelcontento/Workspace/foo/%s" % name.replace("avalon/", "")
    git_ref = "HEAD"

    debug("Add %s as submodule" % name)
    for chunk in git("submodule", "add", "-f", git_url, git_dir, _iter=True):
        info(chunk, end="")

    debug("Switch %s to the right branch" % name)
    for chunk in git("checkout", git_ref, _iter=True, _cwd=git_dir):
        info(chunk, end="")

    debug("Initialize submodules of %s" % name)
    for chunk in git("submodule", "update", "--init", "--recursive", _iter=True, _cwd=git_dir):
        info(chunk, end="")
