# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from sh import git, mkdir
from path import path

from ..cli import info, error
from ..utils import config

TEMPLATES_DIR = path("cocowizard/templates").realpath()

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

    project_name = "".join(parts[2:])

    destination_dir = path(project_name)
    project_dir = destination_dir / "projects" / project_name
    if destination_dir.exists():
        error("Directory '" + destination_dir + "' already exists.")

    _clone_cocos2d_repo(destination_dir, args.cocos_repo_url, args.branch_name)
    _create_project_folders(project_dir)
    _create_default_cocosbuilder_project(project_dir)
    _create_default_metafiles(project_dir)
    _create_default_configuration(project_dir, project_name, package_name)
    _create_git_repo(project_dir)

def _clone_cocos2d_repo(destination_dir, cocos_repo_url, branch_name):
    info("Initialize cocos2d-x repository")
    git("clone", "--verbose" ,"--branch", branch_name, cocos_repo_url, destination_dir)

def _create_project_folders(project_dir):
    info("Initialize assets...")
    (project_dir / "Assets").makedirs_p()

def _create_default_cocosbuilder_project(project_dir):
    info("Initialize CocosBuilder project")
    path(TEMPLATES_DIR / "CocosBuilder").copytree(project_dir / "Assets" / "CocosBuilder")

def _create_default_metafiles(project_dir):
    info("Initialize Metafiles")
    path(TEMPLATES_DIR / "Meta").copytree(project_dir / "Meta")

def _create_default_configuration(project_dir, project_name, package_name):
    info("Initialize yaml configuration")
    text = (TEMPLATES_DIR / "Configuration/cocowizard.yml").text()
    text = text.replace("{project_name}", project_name)
    text = text.replace("{package_name}", package_name)
    (project_dir / "cocowizard.yml").write_text(text)

def _create_git_repo(project_dir):
    git("init", _cwd=project_dir)
    git("add", ".", _cwd=project_dir)
    git("commit", m="cocowizard: initial commit", _cwd=project_dir)
