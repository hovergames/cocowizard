# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh
from path import path

from ..utils import config
from ..utils.log import debug, error

COCOWIZARD_PROJECT = "projects_cocowizard"

def run():
    config.fail_on_missing_config()

    _remove_cocowizard_projects()
    _create_project()
    _move_project_files()
    _remove_cocowizard_projects()

def _project_path():
    cocos2dx_path = path(config.get("general.cocos2dx"))
    return cocos2dx_path / "projects" / COCOWIZARD_PROJECT

def _create_project():
    package = config.get("general.package")
    project = config.get("general.project")

    cocos2dx_path = path(config.get("general.cocos2dx"))
    creator_dir = cocos2dx_path / "tools" / "project-creator"
    creator_orig = creator_dir / "create_project.py"

    debug("execute: %s" % creator_orig)
    creator = sh.Command(creator_orig)
    stdout = creator(n=project, k=package, l="cpp", p=_project_path(), _cwd=creator_dir)

    if "Have Fun!" not in stdout:
        debug(stdout)
        error("Run of create_project.py failed")

def _move_project_files():
    project = config.get("general.project")
    from_dir = _project_path() / project
    to_dir = path("./").realpath()

    # -- Remove all old project directories

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

    # -- Remove some known cocos2d files/folders

    for rmfile in ["CMakeLists.txt"]:
        rmfile = to_dir / rmfile
        if rmfile.exists():
            debug("remove: %s" % rmfile)
            rmfile.remove()

    for rmdir in ["cocos2d"]:
        rmdir = to_dir / rmdir
        if rmdir.exists():
            debug("remove: %s" % rmdir)
            rmdir.rmtree_p()

    # -- And finally copy all new files

    for from_other_dir in from_dir.glob("*"):
        to_other_dir = to_dir / from_other_dir.name
        if not to_other_dir.exists():
            debug("import: %s" % from_other_dir)
            from_other_dir.move(to_other_dir)

def _remove_cocowizard_projects():
    projects_dir = _project_path()
    debug("remove: %s" % projects_dir)
    projects_dir.rmtree_p()
