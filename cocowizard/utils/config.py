# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from yaml import load as yaml_load
from copy import deepcopy

from ..cli import error

CONFIG_NAME = "cocowizard.yml"
CACHE = None

def fail_on_missing_config():
    if not exists():
        error("No project configuration found -- run init first")

def exists():
    global CONFIG_NAME
    return path(CONFIG_NAME).exists()

def root():
    global CACHE
    if CACHE is None:
        CACHE = _load()
    return CACHE

def get(key):
    parts = key.split(".")
    config = root()

    for part in parts:
        if part not in config:
            error(key + " is not configured yet")
        config = config[part]

    return config

# see: http://www.xormedia.com/recursively-merge-dictionaries-in-python/
def _dict_merge(a, b):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and b have a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.'''
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
                result[k] = _dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

def _load():
    fail_on_missing_config()

    global_config = dict()
    local_config = dict()

    global_config_file = path("$HOME").expand() / "." + CONFIG_NAME
    if global_config_file.exists():
        global_stream = open(global_config_file, 'r')
        global_config = yaml_load(global_stream)

    local_config_file = path(CONFIG_NAME)
    if local_config_file.exists():
        local_stream = open(local_config_file, 'r')
        local_config = yaml_load(local_stream)

    if local_config is None:
        return global_config
    else:
        return _dict_merge(global_config, local_config)
