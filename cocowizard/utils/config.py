# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from path import path
from yaml import load as yaml_load

from .log import error

CACHE = dict()

def android_flavors():
    return ["google", "samsung", "amazon"]

def root_dir():
    return (path(sys.argv[0]) / "..").abspath().dirname().realpath()

def from_file(filename):
    global CACHE
    if not filename in CACHE:
        CACHE[filename] = Config(filename)
    return CACHE[filename]

def has(key):
    return from_file("cocowizard.yml").has(key)

def get(key, default=None):
    return from_file("cocowizard.yml").get(key, default)

def dependencies():
    return from_file("cocowizard.yml").dependencies()

def apple_frameworks():
    return from_file("cocowizard.yml").apple_frameworks()

class Config(object):
    def __init__(self, filename):
        filename = path(filename)
        if not filename.exists():
            error("Unable to load config from %s" % filename)

        stream = open(filename, 'r')
        self.config = yaml_load(stream)

        if self.config is None:
            self.config = dict()

    def has(self, key):
        parts = key.split(".")
        config = self.config

        for part in parts:
            if not isinstance(config, dict) or part not in config:
                return False
            config = config[part]

        return True

    def get(self, key, default=None):
        parts = key.split(".")
        config = self.config

        for part in parts:
            if not isinstance(config, dict) or part not in config:
                if not default is None:
                    return default
                else:
                    error(key + " is not configured yet")
            config = config[part]

        return config

    def dependencies(self):
        deps = self.config.get("dependencies", [])
        if isinstance(deps, str):
            return self._name_to_tuple(deps)
        elif isinstance(deps, list):
            deps = map(self._convert_entries, deps)
            deps = [x[0] for x in deps]
            return deps
        else:
            error("Config dependency must be a list")

    def apple_frameworks(self):
        frameworks = self.config.get("apple_frameworks", [])
        if isinstance(frameworks, str):
            frameworks = [str]

        result = []
        for framework in frameworks:
            if isinstance(framework, str):
                name = framework
                required = True
            else:
                name = framework.keys()[0]
                required = framework[name].get("required", True)
            result.append((name, required))

        return result

    def _name_to_tuple(self, name):
        name = name.lower()
        url = "git@github.com:%s.git" % name
        ref = "HEAD"
        return [(name, url, ref)]

    def _convert_entries(self, entry):
        if isinstance(entry, str):
            return self._name_to_tuple(entry)
        elif isinstance(entry, dict):
            name = entry.keys()[0]
            entry = entry[name]

            name, url, ref = self._name_to_tuple(name)
            url = entry.get("url", url)
            ref = entry.get("ref", ref)

            return (name, url, ref)
        else:
            error("Dependency record must be from type str or dict")
