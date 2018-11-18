#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import os
import yaml


class Config(object):
    def __init__(self, file=os.path.join(os.path.dirname(__file__), "config.yml")):
        self._file = file
        self._config = self.read()

    def get(self, key):
        if key in self._config:
            return self._config.get(key)
        else:
            raise Exception("Get config:({key}) failed: this config does not exist!".format(key=key))

    def update(self, key, value):
        if key in self._config:
            self._config[key] = value
            self.write(self._config)
        else:
            raise Exception("Update config:({key}) failed: this config does not exist!".format(key=key))

    def read(self):
        with open(self._file) as f:
            return yaml.load(f)

    def write(self, config):
        with open(self._file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)


globel_config = Config()


def get(key):
    return globel_config.get(key)


def update(key, value):
    globel_config.update(key, value)


if __name__ == "__main__":
    pass
