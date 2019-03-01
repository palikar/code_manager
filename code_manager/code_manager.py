#!/usr/bin/python

import os
import sys
import argparse
import json
import configparser
import locale
from shutil import copyfile
import shutil


import code_manager
from code_manager.utils import flatten
from code_manager.core import Core
from code_manager.version import VERSION

VERSION_MSG = [
    'code-manager version: {0}'.format(VERSION),
    'Python version: {0}'.format(' '.join(line.strip() for line in sys.version.splitlines())),
    'Locale: {0}'.format('.'.join(str(s) for s in locale.getlocale())),
]



cache=None
config=None
usr_dir=None
code_dir=None

def get_arg_parser():

    parser = argparse.ArgumentParser(
        prog="code-mananger",
        description='Installs system packages from the INTERNET!!')

    parser.add_argument('--version', '-v', action="version", version=('\n'.join(VERSION_MSG)),
                        help='Print veriosn inormation')

    parser.add_argument('--code-dir', dest='code_dir', action='store', required=False,
                        help='A folder to put the source of the packages')

    parser.add_argument('--usr-dir', dest='usr_dir', action='store', required=False,
                        help='A folder to install the packages')

    parser.add_argument('--packages-file', dest='packages_file', action='store',
                        help='File to read the packages from', metavar='packages.json')


    parser.add_argument('--setup-only', dest='setup', action="store_true", default=False,
                        help='Only copy the config files if needed')


    subparsers = parser.add_subparsers(title='Commands', description='A list of avialble commands', dest='command', metavar='Command')

    parser_install = subparsers.add_parser('install',description='Full installatio of packages', help='Installs packages (fetch, build and install)')
    parser_install.add_argument('packages', nargs='*',  default=None, help='A list of packages to install')
    parser_install.add_argument('--reinstall', dest='reinstall', action='store_true', help='Should the packages be reinstalled')
    parser_install.add_argument('--group', action='store',metavar='name',default=None, help='Should the packages be reinstalled')

    parser_fetch = subparsers.add_parser('fetch', description='Downloads packages but it does not install them nor build them', help='Downloads packages')
    parser_fetch.add_argument('packages', nargs='*', default=None, help='A list of packages to fetch')
    parser_fetch.add_argument('--focre--clear', dest='force_clear', action='store_true', default=False,
                        help='Will delete any folders that stay on its way')
    parser_fetch.add_argument('--group', action='store',metavar='name',default=None, help='If given, every package from this group will be fetched')

    parser_build = subparsers.add_parser('build', description='Builds a package from source', help='Builds the project of package')
    parser_build.add_argument('packages', nargs='*',  default=None, help='A list of packages to fetch')
    parser_build.add_argument('--group', action='store', metavar='name',default=None, help='If given, every package from this group will be build')
    parser_build.add_argument('--no-install', dest='noinstall', action='store_true', default=False,
                        help='If present, packages will only be build but not installed')

    parser_list_packages = subparsers.add_parser('list-packages', description='Lists the installed packages', help='Lists the installed packages')
    parser_list_cach = subparsers.add_parser('list-cache', help='Show the entries in the cache')
    parser_clear_cache = subparsers.add_parser('clear-cache', help='Clears the entries in the cach file')


    return parser




def install(args,core):

    if args.group is None:
        print(args.packages)
        core.install(args.packages, 
                     reinstall=args.reinstall)
    else:
        core.install_group(args.group, 
                     reinstall=args.reinstall)

3    

def fetch(args,core):
    pass

def build(args,core):
    pass

def list_packages(args,core):
    
    print("Available packages:")
    for pack in flatten(config['packages_list']):
        print(pack)
    


def list_cache(args,core):

    print(f"Dumping cache file {cache}")
    f = open(cache, "r")
    cont = f.read()
    print(cont)
    f.close()


def clear_cache(args,core):

    print(f"Clearing cache file {cache}")
    f = open(cache, "w")
    f.close()


def get_commands_map():

    commands = dict()

    commands['install'] = install
    commands['fetch'] = fetch
    commands['build'] = build
    commands['list-packages'] = list_packages
    commands['list-cache'] = list_cache
    commands['clear-cache'] = clear_cache

    return commands

def main():

    global cache
    global config
    global usr_dir
    global code_dir

    parser = get_arg_parser()

    args = parser.parse_args()
    opt = configparser.ConfigParser()

    private_data_dir = os.path.join(code_manager.CMDIR, "data")

    if not os.path.isdir(code_manager.CONFDIR):
        os.mkdir(code_manager.CONFDIR)
    if not os.path.isfile(os.path.join(code_manager.CONFDIR, "packages.json")):
        copyfile(os.path.join(private_data_dir, "packages.json"),
                 os.path.join(code_manager.CONFDIR, "packages.json"))

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
    if not os.path.isfile(cache):
        print(cache)
        f = open(cache, 'a+')
        f.close()

    if not os.path.isdir(usr_dir):
        os.makedirs(usr_dir)
    if not os.path.isdir(code_dir):
        os.makedirs(code_dir)



    print(f"Code dir: {code_dir}")
    print(f"Usr dir: {usr_dir}")
    print(f"Packages file: {packages_file}")
    print(f"Install script directory: {install_scripts_dir}")
    print(f"Cache file: {cache}")

    with open(packages_file, "r") as config_file:
        config = json.load(config_file)
        
    if args.setup:
        print("Setup for config files done. Exiting now! ")
        exit(0)

    if args.command is None:
        parser.print_help()
        exit(1)

    commands = get_commands_map()

    
    core = Core(False, cache, config, code_dir, usr_dir,
                install_scripts_dir, False)
    
    commands[args.command](args, core)



if __name__ == '__main__':
    main()
