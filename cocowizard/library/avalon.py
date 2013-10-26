# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from sh import git

from ..cli import info, warning, debug

AVALON_URL = "git@github.com:hovergames/avalon.git"

def run():
    _ensure_installed()
    _configure_android()
    _configure_ios()

def _ensure_installed():
    vendors_dir = path("Vendors").realpath()
    vendors_dir.mkdir_p()

    avalon_dir = vendors_dir / "avalon"
    avalon_git_dir = avalon_dir / ".git"

    if not avalon_dir.exists():
        _add_git_submodule(avalon_dir)
    elif not avalon_git_dir.exists():
        warning("Avalon vendor folder exists but it's NOT managed with git!")
    elif avalon_git_dir.isdir():
        warning("Avalon vendor folder it's NOT a git submodule!")

def _add_git_submodule(avalon_dir):
    info("adding avalon with all submodules -- this can take a while")
    warning("do not interrupt this process!")

    debug("add avalon as submodule")
    for chunk in git("submodule", "add", AVALON_URL, avalon_dir, _iter=True):
        info(chunk, end="")

    debug("initialize submodules inside of avalon")
    for chunk in git("submodule", "update", "--init", "--recursive", _iter=True, _cwd=avalon_dir):
        info(chunk, end="")

def _configure_android():
    pass

def _configure_ios():
    pass
