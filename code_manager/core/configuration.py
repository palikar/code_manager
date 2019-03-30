from __future__ import (absolute_import, division, print_function)

import logging
import re


from code_manager.utils.utils import flatten

def recursive_items(dictionary, dicts=False):
    if type(dictionary) is dict:
        for key, value in dictionary.items():
            if type(value) is dict:
                if dicts:
                    yield (key, value)
                    yield from recursive_items(value, dicts = dicts)
                else:
                    yield from recursive_items(value, dicts = dicts)
            elif type(value) is list:
                for v in value:
                    if type(v) is dict or type(v) is list:
                        yield from recursive_items(v, dicts = dicts)
                yield (key, value)
            else:
                yield (key, value)
    elif type(dictionary) is list:
        for v in dictionary:
            if type(v) is dict or type(v) is list:
                yield from recursive_items(v, dicts = dicts)
        yield (None, dictionary)


class CofigurationResolver(object):

    _VAR_RE = re.compile(r'(@\w+)|(\\@)')
    _VAR_NAME_RE = re.compile(r'\w+')
    config = None
    variables = {}

    PACKAGES_LIST_NODE = "packages_list"
    PACKAGES_NODE = "packages"
    VARS_NODE = "vars"

    def __init__(self):
        pass


    def _check_integrity(self, config):
        
        success = True
        if "packages_list" not in config.keys():
            logging.debug('The \'packages_list\' is missing in the package file')
            success = False

        if "packages" not in config.keys():
            logging.debug('The \'packages\' is missing in the package file')
            success = False

        if "vars" in config.keys():

            if type(config['vars']) is not dict:
                    logging.debug('The \'vars\' are not an proper object.')
                    success = False

            for var,val in config['vars'].items():
                if not self._VAR_NAME_RE.fullmatch(var):
                    logging.debug('The variable \'{0}\' has invalid identifier.'.format(var))
                    success = False
                if type(val) is not str:
                    logging.debug('The variable \'{0}\' has invalid value \'{1}\'.'.format(var, val))
                    success = False




        packages_list = flatten(config['packages_list'].values())
        for pack in packages_list:
            if pack not in config['packages'].keys():
                logging.debug('The \'{0}\' packages is in the list but does not have a node'.format(pack))
                success = False

        return success


    def _resolve_string(self, string):
        for match in self._VAR_RE.finditer(string):
            if match.group(1) is not None:
                var = match.group(1)[1:]
                value =  self.variables[var]
                return string.replace(match.group(1), value)
            if match.group(2) is not None:
                return string.replace('\\@','')

    def configuration_dict(self, config):
        self.config = config

        if not self._check_integrity(config):
            logging.debug('The package file has some issues.')
            raise SystemExit


        if 'vars' in config.keys():
            self.variables = config['vars']
            config.pop('vars')

        cur_dicts = {}
        for key, value in recursive_items(config, dicts=True):

            if isinstance(value, dict):
                cur_dicts = value
            else:
                if isinstance(value, list):
                    for idx, item in enumerate(value):
                        if not isinstance(item, list) and not isinstance(item, dict):
                            new_val = self._resolve_string(item)
                            if new_val is not None and new_val != value:
                                value[idx] = new_val
                else:
                    new_val = self._resolve_string(value)
                    if new_val is not None and new_val != value:
                        cur_dicts[key] = new_val



class ConfigurationAware(object):

    @staticmethod
    def var(name):
        if name in ConfigurationAware.resovler.variables.keys():
            return ConfigurationAware.resovler.variables[name]
        else:
            return None

    @staticmethod
    def var_check(name):
        return name in ConfigurationAware.resovler.variables.keys()

    @staticmethod
    def set_configuration(config, install_scripts_dir, cache_file, opt):

        ConfigurationAware.opt = opt
        ConfigurationAware.usr_dir = opt["Config"]["code"]
        ConfigurationAware.code_dir = opt["Config"]["usr"]

        ConfigurationAware.resovler = CofigurationResolver()
        ConfigurationAware.config = ConfigurationAware.resovler.configuration_dict(config)

        ConfigurationAware.install_scripts_dir = install_scripts_dir

        ConfigurationAware.cache_file = cache_file
