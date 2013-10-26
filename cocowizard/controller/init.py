# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import shutil
from sh import git, mkdir
from path import path

from ..cli import info, error
from ..utils import config

TEMPLATES_DIR = path("cocowizard/templates").realpath()

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("packageName", help="Specify the package name.")
    parser.add_argument("cocosRepoUrl", help="Specify the cocos2d-x git repository url.")
    parser.add_argument("branchName", help="Which branch of cocos2d-x do you want to use?")
    args = parser.parse_args()

    packageName = args.packageName
    parts = packageName.split(".")
    if len(parts) < 2:
        error("Package name invalid: Use format com.company.projectName")

    parts.pop(0)
    parts.pop(0)
    projectName = "".join(parts)

    destinationDir = projectName
    projectDir = destinationDir + "/projects/" + projectName

    if os.path.exists(os.path.join(os.getcwd(), destinationDir)):
        error("Directory '" + destinationDir + "' already exists.")

    _cloneCocos2dRepo(destinationDir, args.cocosRepoUrl, args.branchName)
    _createProjectFolders(projectDir)
    _createDefaultCocosbuilderProject(projectDir)
    _createDefaultMetafiles(projectDir)
    _createDefaulConfiguration(projectDir, projectName, packageName)

def _cloneCocos2dRepo(destinationDir, cocosRepoUrl, branchName):
    info("Initialize cocos2d-x repository")
    git("clone", "--verbose" ,"--branch", branchName, cocosRepoUrl, destinationDir)

def _createProjectFolders(projectDir):
    info("Initialize assets...")
    path(projectDir + "/Assets").makedirs_p()

def _createDefaultCocosbuilderProject(projectDir):
    info("Initialize CocosBuilder project")
    path(TEMPLATES_DIR / "CocosBuilder").copytree(projectDir + "/Assets" + "/CocosBuilder")

def _createDefaultMetafiles(projectDir):
    info("Initialize Metafiles")
    path(TEMPLATES_DIR / "Meta").copytree(projectDir + "/Meta")

def _createDefaulConfiguration(projectDir, projectName, packageName):
    info("Initialize yaml configuration")
    text = path(TEMPLATES_DIR / "Configuration/cocowizard.yml").text()
    text = text.replace("{projectName}", projectName)
    text = text.replace("{packageName}", packageName)
    path(projectDir + "/cocowizard.yml").write_text(text)
