#!/usr/bin/python

import os
import sys
import argparse
import json
import subprocess
import configparser
import locale
from shutil import copyfile
import shutil


import code_manager
from code_manager.core import Core
from code_manager.utils import flatten
from code_manager.version import VERSION

VERSION_MSG = [
    'code-manager version: {0}'.format(VERSION),
    'Python version: {0}'.format(' '.join(line.strip() for line in sys.version.splitlines())),
    'Locale: {0}'.format('.'.join(str(s) for s in locale.getlocale())),
]


def main():

    parser = argparse.ArgumentParser(
        prog="code-mananger",
        description='Installs system packages from the INTERNET!!')

    parser.add_argument('--version', '-v', action="version", version=('\n'.join(VERSION_MSG)),
                        help='Print veriosn inormation')

    parser.add_argument('--setup-only', dest='setup', action="store_true", default=False,
                        help='Only copy the config files if needed')

    parser.add_argument('--list-packages', dest='list_pack', action="store_true", default=False,
                        help='List the available packages in the packages.json file')

    parser.add_argument('--clear-cache', dest='clear_cache', action="store_true", default=False,
                        help='Clears the entries in the cach file')

    parser.add_argument('--install', dest='packages',
                        help='Packages to install', nargs='+')

    parser.add_argument('--reinstall', dest='reinstall',
                        help='Packages to reinstall', nargs='+')

    parser.add_argument('--code-dir', dest='code_dir', action='store', required=False,
                        help='A folder to put the source of the packages')

    parser.add_argument('--usr-dir', dest='usr_dir', action='store', required=False,
                        help='A folder to install the packages')

    parser.add_argument('--packages-file', dest='packages_file', action='store',
                        help='File to read the packages from')

    parser.add_argument('--install-all', dest='inst_all', action='store', type=int, default=None, nargs='?',
                        const=-1, help='Install all packages in --packages from the given group')

    parser.add_argument('--reinstall-all', dest='reall', action='store', type=int, default=None, nargs='?',
                        const=-1, help='Reinstall all packages in --packages from the given group')

    parser.add_argument('--no-install', dest='noinstall', action='store_true', default=False,
                        help='If present, packages will only be downloaded')

    args = parser.parse_args()
    opt = configparser.ConfigParser()

    private_data_dir = os.path.join(code_manager.CMDIR, "data")

    if not os.path.isdir(code_manager.CONFDIR):
        os.mkdir(code_manager.CONFDIR)
    if not os.path.isfile(os.path.join(code_manager.CONFDIR, "packages.json")):
        copyfile(os.path.join(private_data_dir, "packages.json"),
                 os.path.join(code_manager.CONFDIR, "packages.json"))

    if not os.path.isfile(os.path.join(code_manager.CONFDIR, "cache")):
        copyfile(os.path.join(private_data_dir, "cache"),
                 os.path.join(code_manager.CONFDIR, "cache"))

    if not os.path.isfile(os.path.join(code_manager.CONFDIR, "conf")):
        copyfile(os.path.join(private_data_dir, "conf"),
                 os.path.join(code_manager.CONFDIR, "conf"))

    if not os.path.isdir(os.path.join(code_manager.CONFDIR, "install_scripts")):
        shutil.copytree(os.path.join(code_manager.CMDIR, "install_scripts"),
                        os.path.join(code_manager.CONFDIR, "install_scripts"))

    install_scripts_dir = os.path.join(code_manager.CONFDIR, "install_scripts")

    opt.read(os.path.join(os.path.join(code_manager.CONFDIR, "conf")))

    if args.code_dir is not None:
        code_dir = os.path.abspath(os.path.expanduser(args.code_dir))
    else:
        code_dir = os.path.abspath(
            os.path.expanduser(os.path.expandvars(opt["Config"]["code"])))

    if args.usr_dir is not None:
        usr_dir = os.path.abspath(os.path.expanduser(args.usr_dir))
    else:
        usr_dir = os.path.abspath(
            os.path.expanduser(os.path.expandvars(opt["Config"]["usr"])))

    if args.packages_file is not None:
        packages_file = os.path.abspath(os.path.expanduser(args.packages_file))
    else:
        packages_file = os.path.join(code_manager.CONFDIR, "packages.json")

    cache = os.path.join(code_manager.CONFDIR, "cache")
    if not os.path.isfile(os.path.isfile(cache)):
        f = open(cache, "w+")
        f.close()

    if not os.path.isdir(usr_dir):
        os.makedirs(usr_dir)
    if not os.path.isdir(code_dir):
        os.makedirs(code_dir)

    print(f"Code dir: {code_dir}")
    print(f"Usr dir: {usr_dir}")
    print(f"Packages file: {packages_file}")
    print(f"Install script directory: {install_scripts_dir}")

    with open(packages_file, "r") as config_file:
        config = json.load(config_file)

    if args.setup:
        print("Setup for config files done. Exiting now! ")
        exit(0)

    if args.list_pack:
        print("Available packages:")
        print(config['packages_list'])
        exit(0)

    if args.clear_cache:
        print(f"Clearing cache file {cache}")
        f = open(cache, "w")
        f.close()
        print("Cleared!")
        exit(0)

    core = Core(args.noinstall, cache, config, code_dir, usr_dir, install_scripts_dir)

    if args.inst_all is not None:
        core.install_all(config, code_dir, group=args.inst_all)
    elif args.reall is not None:
        core.install_all(config, code_dir, group=args.reall, reinstall=True)
    else:
        core.install(config, code_dir, args.packages)
        core.install(config, code_dir, args.reinstall, reinstall=True)


if __name__ == '__main__':
    main()
