# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh
from path import path

from ..utils import config
from ..cli import debug, error

CREATOR_DIR = path("../../tools/project_creator").realpath()
CREATOR_ORIG = (CREATOR_DIR / "create_project.py")
CREATOR_WIZARD = (CREATOR_DIR / "create_project_wizard.py")
COCOWIZARD_PROJECT = "projects_cocowizard"

def run():
    _patch_project_creator()
    _remove_cocowizard_projects()
    _create_project()
    _remove_patched_project_creator()
    _move_project_files()
    _remove_cocowizard_projects()

def _patch_project_creator():
    search = ', "projects", '
    replace = ', "' + COCOWIZARD_PROJECT + '", '

    text = CREATOR_ORIG.text()
    if search not in text:
        error("Unable to patch project_creator.py")
    text = text.replace(search, replace)

    debug("create: " + CREATOR_WIZARD)
    CREATOR_ORIG.copy(CREATOR_WIZARD)

    debug("patch: " + CREATOR_WIZARD)
    CREATOR_WIZARD.write_text(text)

def _create_project():
    package = config.get("general.package")
    project = config.get("general.project")

    debug("execute: " + CREATOR_WIZARD)
    creator = sh.Command(CREATOR_WIZARD)
    stdout = creator(p=project, k=package, l="cpp", _cwd=CREATOR_DIR)

    if "Have Fun!" not in stdout:
        debug(stdout)
        error("Run of create_project.py failed")

def _remove_patched_project_creator():
    debug("remove: " + CREATOR_WIZARD)
    CREATOR_WIZARD.remove()

def _move_project_files():
    project = config.get("general.project")
    from_dir = path("../../" + COCOWIZARD_PROJECT).realpath() / project
    to_dir = path("./").realpath()

    for proj_dir in to_dir.glob("proj.*"):
        debug("remove: " + proj_dir)
        proj_dir.rmtree()

    for proj_dir in from_dir.glob("proj.*"):
        debug("import: " + proj_dir)
        proj_dir.move(to_dir)

    android_dir = to_dir / "proj.android"
    for android_flavor in ["samsung", "amazon", "google"]:
        proj_dir = to_dir / "proj.android." + android_flavor
        debug("copy: " + proj_dir)
        android_dir.copytree(proj_dir)
    android_dir.rmtree_p()

def _remove_cocowizard_projects():
    projects_dir = path("../../" + COCOWIZARD_PROJECT).realpath()
    debug("remove: " + projects_dir)
    projects_dir.rmtree()
