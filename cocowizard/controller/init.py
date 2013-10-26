# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import shutil

from ..cli import info
from ..cli import error
from ..utils import config

from sh import git
from sh import mkdir
from path import path

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("projectName", 	help="Specify an project name.")
    parser.add_argument("cocosRepoUrl", help="Specify the cocos2d-x git repository url.")
    parser.add_argument("branchName", 	help="Which branch of cocos2d-x do you want to use?")
    args = parser.parse_args()

    destinationDir = args.projectName
    projectDir = destinationDir + "/projects/" + args.projectName

    if (os.path.exists(os.path.join(os.getcwd(), destinationDir))):
	    error("Directory '" + destinationDir + "' already exists.")

    _cloneCocos2dRepo(destinationDir, args.cocosRepoUrl, args.branchName)
    _createProjectFolders(projectDir)
    _createDefaultCocosbuilderProject(projectDir)

def _cloneCocos2dRepo(destinationDir, cocosRepoUrl, branchName):
    for chunk in git("clone", "--verbose" ,"--branch", branchName, cocosRepoUrl, destinationDir, _iter = True, _out_bufsize = 1):
    	print(chunk)

def _createProjectFolders(projectDir):
    path(projectDir + "/Assets").makedirs_p()

def _createDefaultCocosbuilderProject(projectDir):
    path("cocowizard/templates/CocosBuilder").copytree(projectDir + "/Assets" + "/CocosBuilder")

def _createDefaultCocosbuilderProject(projectDir):
    path("cocowizard/templates/Meta").copytree(projectDir + "/Meta")
