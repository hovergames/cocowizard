# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from itertools import ifilter, imap
from functools import partial
from path import path
import sh

from ..utils import config
from ..utils.log import error, warning

# TODO: Move this to utils.tools.monkeywizard!
monkeywizard = sh.Command(path("$HOME/Workspace/private/monkey-wizard/wizard.build/stdcpp/main_macos").expand())

def run():
    _configure_ios()
    for flavor in ["amazon", "google", "samsung"]:
        _configure_android(flavor)

def _configure_ios():
    warning("iOS support currently disabled!")
    return

    icons_dir = path("Meta/_generated/ios")
    if not icons_dir.exists():
        error("No iOS icons generated yet -- try cocowizard generate_icons")

    proj_dir = path("proj.ios_mac").realpath()
    if not proj_dir.exists():
        error("No iOS project generated yet -- try cocowizard update")

    prerendered = config.get("icons.ios.settings.prerendered")
    store_icon = lambda x: "1024" not in x
    single_quotes = lambda x: "'%s'" % x
    realpath = lambda x : x.realpath()

    files = icons_dir.glob("*")
    files = ifilter(store_icon, files)
    files = imap(realpath, files)
    files = imap(single_quotes, files)
    files = " ".join(files)

    monkeywizard("IosIcons", single_quotes(proj_dir), int(prerendered), files)

def _configure_android(flavor):
    icons_dir = path("Meta/_generated/android.%s" % flavor)
    if not icons_dir.exists():
        error("No android icons generated yet -- try cocowizard generate_icons")

    proj_dir = path("proj.android.%s" % flavor).realpath()
    if not proj_dir.exists():
        error("No android project generated yet -- try cocowizard update")

    add_icon = partial(monkeywizard, "AndroidIcons", proj_dir)
    get_icon = lambda x: icons_dir / "icon-%s.png" % x

    add_icon("low", get_icon(36))
    add_icon("medium", get_icon(48))
    add_icon("high", get_icon(72))
    add_icon("extra-high", get_icon(96))
