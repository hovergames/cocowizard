# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import sh
from path import path

from ..utils import config
from ..utils.log import debug, error

CREATOR_DIR = path("../../tools/project-creator").realpath()
CREATOR_ORIG = (CREATOR_DIR / "create_project.pyw")
CREATOR_CORE = (CREATOR_DIR / "module" / "core.py")
COCOWIZARD_PROJECT = "projects_cocowizard"

def run():
    config.fail_on_missing_config()

    _patch_project_creator()
    _remove_cocowizard_projects()
    _create_project()
    _move_project_files()
    _remove_cocowizard_projects()

def _patch_project_creator():
    search = 'ignoreList={'
    replace = 'ignoreList = { "projects": None, "projects_cocowizard": None,'

    text = CREATOR_CORE.text()
    if search not in text:
        if replace in text:
            return
        error("Unable to patch project_creator.py")
    text = text.replace(search, replace)

    CREATOR_CORE.write_text(text)

def _create_project():
    package = config.get("general.package")
    project = config.get("general.project")

    debug("execute: %s" % CREATOR_ORIG)
    creator = sh.Command(CREATOR_ORIG)
    project_path = "../../" + COCOWIZARD_PROJECT

    stdout = creator(n=project, k=package, l="cpp", p=project_path, _cwd=CREATOR_DIR)

    if "Have Fun!" not in stdout:
        debug(stdout)
        error("Run of create_project.py failed")

def _move_project_files():
    project = config.get("general.project")
    from_dir = path("../../%s" % COCOWIZARD_PROJECT).realpath() / project
    to_dir = path("./").realpath()

    for proj_dir in to_dir.glob("proj.*"):
        debug("remove: %s" % proj_dir)
        proj_dir.rmtree()


    for proj_dir in from_dir.glob("proj.*"):
        debug("import: %s" % proj_dir)
        proj_dir.move(to_dir)

    android_dir = to_dir / "proj.android"
    for android_flavor in config.android_flavors():
        proj_dir = to_dir / "proj.android.%s" % android_flavor
        debug("copy: %s" % proj_dir)
        android_dir.copytree(proj_dir)
    android_dir.rmtree_p()

    for from_other_dir in from_dir.glob("*"):
        to_other_dir = to_dir / from_other_dir.name
        if not to_other_dir.exists():
            debug("import: %s" % from_other_dir)
            from_other_dir.move(to_other_dir)

def _remove_cocowizard_projects():
    projects_dir = path("../../%s" % COCOWIZARD_PROJECT).realpath()
    debug("remove: %s" % projects_dir)
    projects_dir.rmtree_p()
