import json
import logging
import os
import re

from code_manager.utils.utils import flatten
from code_manager.utils.utils import recursive_items


class CofigurationResolver:

    _VAR_RE = re.compile(r'@(\w+)?@|(\\@)')
    _VAR_NAME_RE = re.compile(r'\w+')
    config = None
    variables = {}

    PACKAGES_LIST_NODE = 'packages_list'
    PACKAGES_NODE = 'packages'
    VARS_NODE = 'vars'

    def __init__(self):
        pass

    def _check_integrity(self, config):

        success = True
        if 'packages_list' not in config.keys():
            logging.debug("The 'packages_list' is missing in the package file")
            success = False

        if 'packages' not in config.keys():
            logging.debug("The 'packages' is missing in the package file")
            success = False

        if 'vars' in config.keys():

            if not isinstance(config['vars'], dict):
                logging.debug("The 'vars' are not an proper object.")
                success = False

            for var, val in config['vars'].items():
                if not self._VAR_NAME_RE.fullmatch(var):
                    logging.debug("The variable '%s' has invalid identifier.", var)
                    success = False
                if not isinstance(val, str):
                    logging.debug("The variable '%s' has invalid value '%s'.", var, val)
                    success = False

        packages_list = flatten(config['packages_list'].values())
        for pack in packages_list:
            if pack not in config['packages'].keys():
                logging.debug(
                    "The '%s' packages is in the list but does\
                not have a node",
                    pack,
                )
                success = False

        return success

    def resolve_string(self, string):
        if not isinstance(string, str):
            return string

        for match in self._VAR_RE.finditer(string):
            if match.group(1) is not None:
                var = match.group(1)
                if var not in self.variables.keys():
                    return string
                value = self.variables[var]
                return string.replace(match.group(0), value)
            if match.group(2) is not None:
                return string.replaceAll('@', '')

        return string

    def configuration_dict(self, config):

        if not self._check_integrity(config):
            logging.debug('The package file has some issues.')
            raise SystemExit

        if 'vars' in config.keys():
            self.variables = config['vars']
            config.pop('vars')

        return self.resolve_nodes(config)

    def resolve_nodes(self, config):
        self.config = config
        cur_dicts = config
        dicts = []
        for key, value in recursive_items(config, dicts=True):

            if isinstance(value, dict):
                dicts.append((value, len(value)))
                cur_dicts = value
            else:

                if isinstance(value, list):
                    for idx, item in enumerate(value):
                        if not isinstance(item, list) and not isinstance(item, dict):
                            new_val = self.resolve_string(item)
                            if new_val is not None and new_val != value:
                                value[idx] = new_val
                else:
                    new_val = self.resolve_string(value)
                    if new_val is not None and new_val != value:
                        cur_dicts[key] = new_val
                if dicts:
                    dicts[-1] = (dicts[-1][0], dicts[-1][1] - 1)

            if dicts:
                if dicts[-1][1] == 0:
                    dicts.pop(-1)
                    if len(dicts) == 0:
                        cur_dicts = config
                    else:
                        cur_dicts = dicts[-1][0]

        return config


class ConfigurationAware:
    @staticmethod
    def _load_extra_pack(primary_config, config):
        primary_config.setdefault('vars', {})
        for var, value in config.get('vars', {}).items():
            primary_config['vars'][var] = value

        primary_config.setdefault('packages_list', {})
        for group_name, group_list in config.get('packages_list', {}).items():
            primary_config['packages_list'].setdefault(group_name, group_list)

        primary_config.setdefault('debian_packages', {})
        for list_name, list_list in config.get('debian_packages', {}).items():
            primary_config['debian_packages'].setdefault(list_name, list_list)

        primary_config.setdefault('packages', {})
        for pack_name, pack_node in config.get('packages', {}).items():
            primary_config['packages'].setdefault(pack_name, pack_node)

        return primary_config

    @staticmethod
    def var(name):
        if name in ConfigurationAware.resovler.variables.keys():
            return ConfigurationAware.resovler.variables[name]
        return None

    @staticmethod
    def var_check(name):
        return name in ConfigurationAware.resovler.variables.keys()

    @staticmethod
    def packages_list():
        return ConfigurationAware.config['packages_list']

    @staticmethod
    def variables():
        return ConfigurationAware.config['vars']

    @staticmethod
    def set_configuration(config, install_scripts_dir, cache_file, opt, extra_configs=[]):

        ConfigurationAware.opt = opt
        ConfigurationAware.usr_dir = os.path.expandvars(opt['Config']['usr'])
        ConfigurationAware.code_dir = os.path.expandvars(opt['Config']['code'])

        ConfigurationAware.resolver = CofigurationResolver()

        if extra_configs:
            for pack in extra_configs:
                with open(pack) as config_file:
                    con = json.load(config_file)
                config = ConfigurationAware._load_extra_pack(config, con)

        ConfigurationAware.config = ConfigurationAware.resolver.configuration_dict(
            config,
        )

        ConfigurationAware.packages_list = ConfigurationAware.config['packages_list']
        ConfigurationAware.packages = ConfigurationAware.config['packages']

        ConfigurationAware.packages_config = ConfigurationAware.config.get('packages_config', {})

        ConfigurationAware.variables = ConfigurationAware.resolver.variables

        ConfigurationAware.install_scripts_dir = install_scripts_dir

        ConfigurationAware.cache_file = cache_file

        ConfigurationAware.debug = (
            'debug' in opt['Config'].keys() and opt['Config']['debug'] == 'true'
        )
        ConfigurationAware.git_ssh = (
            'git_ssh' in opt['Download'].keys() and opt['Download']['git_ssh'] == 'true'
        )

    def __getattr__(self, item):
        opt = ConfigurationAware.opt
        if item in opt.get('Common', {}).keys():
            return opt['Common'][item]
        return None
