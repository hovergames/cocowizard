# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from sh import git, mkdir
from path import path

from ..utils.config import root_dir
from ..utils.log import debug, error, info

TEMPLATES_DIR = root_dir() / "cocowizard" / "templates"

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_name", help="Specify the package name.")
    parser.add_argument("cocos_repo_url", help="Specify the cocos2d-x git repository url.")
    parser.add_argument("branch_name", help="Which branch of cocos2d-x do you want to use?")
    args = parser.parse_args()

    package_name = args.package_name
    parts = package_name.split(".")
    if len(parts) < 2:
        error("Package name invalid: Use format com.company.project_name")

    project_name = ".".join(parts[2:])
    destination_dir = path(project_name)
    project_dir = destination_dir / "projects" / project_name
    if destination_dir.exists():
        error("Directory '%s' already exists." % destination_dir)

    _clone_cocos2d_repo(destination_dir, args.cocos_repo_url, args.branch_name)
    _create_project_folder(project_dir)
    _create_default_configuration(project_dir, project_name, package_name)
    _create_git_repo(project_dir)

    info("Now go and run 'cocowizard update' in your new project!")

def _clone_cocos2d_repo(destination_dir, cocos_repo_url, branch_name):
    debug("Initialize cocos2d-x repository")
    git("clone", "--verbose" ,"--branch", branch_name, cocos_repo_url, destination_dir)

def _create_project_folder(project_dir):
    debug("Copy base project files")
    (TEMPLATES_DIR / "project").copytree(project_dir)

def _create_default_configuration(project_dir, project_name, package_name):
    debug("Initialize yaml configuration")
    yml_file = project_dir / "cocowizard.yml"
    text = yml_file.text()
    text = text.replace("{project_name}", project_name)
    text = text.replace("{package_name}", package_name)
    yml_file.write_text(text)

def _create_git_repo(project_dir):
    debug("Initialize git repository and first commit")
    git("init", _cwd=project_dir)
    git("add", ".", _cwd=project_dir)
    git("commit", m="cocowizard: initial commit", _cwd=project_dir)
