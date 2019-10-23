#!/usr/bin/env python

from shutil import copyfile, copytree
import os
import sys
import argparse
import json
import configparser
import locale
import logging
import code_manager

from code_manager.core.manager import Manager
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.utils import flatten
from code_manager.utils.logger import setup_logging
from code_manager.version import VERSION


VERSION_MSG = [
    "code-manager version: {0}".format(VERSION),
    "Python version: {0}".format(
        " ".join(line.strip() for line in sys.version.splitlines())),
    "Locale: {0}".format(".".join(str(s) for s in locale.getlocale())),
]

# pylint: disable=W0603
CACHE = None
CONFIG = None
USR_DIR = None
CODE_DIR = None
INSTALL_SCRIPTS_DIR = None
PACKAGES_FILE = None


def get_arg_parser():

    parser = argparse.ArgumentParser(
        prog="code-mananger", description="Installs system packages from the INTERNET!!"
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=("\n".join(VERSION_MSG)),
        help="Print veriosn inormation",
    )

    parser.add_argument(
        "--code-dir",
        dest="code_dir",
        action="store",
        required=False,
        help="A folder to put the source of the packages",
    )

    parser.add_argument(
        "--usr-dir",
        dest="usr_dir",
        action="store",
        required=False,
        help="A folder to install the packages",
    )

    parser.add_argument(
        "--packages-file",
        dest="packages_file",
        action="store",
        help="File to read the packages from",
        metavar="packages.json",
    )

    parser.add_argument(
        "--setup-only",
        dest="setup",
        action="store_true",
        default=False,
        help="Only copy the config files if needed",
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Run in debug mode outputing more information",
    )

    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Print a lot of information about the execution.",
    )

    subparsers = parser.add_subparsers(
        title="Commands",
        description="A list\
        of avialble commands",
        dest="command",
        metavar="Command",
    )

    parser_install = subparsers.add_parser(
        "install",
        description="Full installatio \
        of packages",
        help="Installs packages \
        (fetch, build and install)",
    )
    parser_install.add_argument(
        "packages", nargs="*", default=None, help="A list of packages to install"
    )
    parser_install.add_argument(
        "--reinstall",
        dest="reinstall",
        action="store_true",
        help="Should the packages be reinstalled",
    )
    parser_install.add_argument(
        "--group",
        action="store",
        metavar='group',
        default=None,
        help="Should the packages be reinstalled",
    )

    parser_fetch = subparsers.add_parser(
        "fetch",
        description="Downloads packages but\
        it does not install them nor builds\
        them. If a name of a group is given,\
        all packages of the group will\
        be downloaded.",
        help="Downloads packages",
    )

    parser_fetch.add_argument(
        "packages", nargs="*", default=None, help="A list of packages to fetch"
    )

    # TODO: Add support for foce clear
    # parser_fetch.add_argument(
    #     "--focre--clear",
    #     dest="force_clear",
    #     action="store_true",
    #     default=False,
    #     help="Will delete anyfolders that stay on its way",
    # )

    parser_fetch.add_argument(
        "--group",
        action="store",
        metavar="name",
        default=None,
        help="If given, every\
        package from this group will be fetched",
    )

    parser_build = subparsers.add_parser(
        "build",
        description="Builds a package\
        from source",
        help="Builds the project of package",
    )
    parser_build.add_argument(
        "packages", nargs="*", default=None, help="A list of packages to fetch."
    )
    parser_build.add_argument(
        "--group",
        action="store",
        metavar="name",
        default=None,
        help="If given, every package\
        from this group will be build",
    )
    parser_build.add_argument(
        "--no-install",
        dest="noinstall",
        action="store_true",
        default=False,
        help="If present, packages will only be build but not installed.",
    )

    subparsers.add_parser(
        "list-packages",
        description="Lists the installed packages",
        help="Lists the installed packages.",
    )
    subparsers.add_parser("list-cache", help="Show the entries in the cache")
    subparsers.add_parser("clear-cache", help="Clears the entries in the cach file")

    return parser


def install(args, core):
    if args.group is not None:
        core.install_thing(args.group, install=True)
    else:
        core.install_thing(args.packages, install=True)


def fetch(args, core):
    if args.group is not None:
        core.install_thing(args.group, fetch=True)
    else:
        core.install_thing(args.packages, fetch=True)


def build(args, core):
    if args.group is not None:
        core.install_thing(args.group, build=True)
    else:
        core.install_thing(args.packages, build=True)


def list_packages(args, core):
    logging.debug("Available packages:")
    for pack in flatten(CONFIG["packages_list"].values()):
        print(pack)


def list_cache(_, core):
    logging.debug("Dumping cache file %s", CACHE)
    handle = open(CACHE, "r")
    cont = handle.read()
    # TODO : Pretty printing; some sort of table
    print(cont)
    handle.close()


def clear_cache(_, core):
    logging.info("Clearing cache file %s", CACHE)
    # TODO : Add "Are you sure check here"; It's too easy now
    handle = open(CACHE, "w")
    handle.close()


def get_commands_map():
    commands = dict()

    commands["install"] = install
    commands["fetch"] = fetch
    commands["build"] = build
    commands["list-packages"] = list_packages
    commands["list-cache"] = list_cache
    commands["clear-cache"] = clear_cache

    return commands


def setup_config_files(args, opt):

    global CACHE
    global CONFIG
    global USR_DIR
    global CODE_DIR
    global INSTALL_SCRIPTS_DIR
    global PACKAGES_FILE

    private_data_dir = os.path.join(code_manager.CMDIR, "data")

    if not os.path.isdir(code_manager.CONFDIR):
        os.mkdir(code_manager.CONFDIR)
    if not os.path.isfile(os.path.join(code_manager.CONFDIR, "packages.json")):
        copyfile(
            os.path.join(private_data_dir, "packages.json"),
            os.path.join(code_manager.CONFDIR, "packages.json"),
        )

    if not os.path.isfile(os.path.join(code_manager.CONFDIR, "conf")):
        copyfile(
            os.path.join(private_data_dir, "conf"),
            os.path.join(code_manager.CONFDIR, "conf"),
        )

    if not os.path.isdir(os.path.join(code_manager.CONFDIR, "install_scripts")):
        copytree(
            os.path.join(code_manager.CMDIR, "install_scripts"),
            os.path.join(code_manager.CONFDIR, "install_scripts"),
        )

    INSTALL_SCRIPTS_DIR = os.path.join(code_manager.CONFDIR, "install_scripts")

    opt.read(os.path.join(os.path.join(code_manager.CONFDIR, "conf")))

    if args.code_dir is not None:
        code_dir = os.path.abspath(os.path.expanduser(args.code_dir))
    else:
        code_dir = os.path.abspath(
            os.path.expanduser(os.path.expandvars(opt["Config"]["code"]))
        )

    if args.usr_dir is not None:
        usr_dir = os.path.abspath(os.path.expanduser(args.usr_dir))
    else:
        usr_dir = os.path.abspath(
            os.path.expanduser(os.path.expandvars(opt["Config"]["usr"]))
        )

    if args.packages_file is not None:
        packages_file = os.path.abspath(os.path.expanduser(args.packages_file))
    else:
        packages_file = os.path.join(code_manager.CONFDIR, "packages.json")

    CACHE = os.path.join(code_manager.CONFDIR, "cache")
    if not os.path.isfile(CACHE):
        logging.info(CACHE)
        handle = open(CACHE, "a+")
        handle.close()

    if not os.path.isdir(usr_dir):
        os.makedirs(usr_dir)
    if not os.path.isdir(code_dir):
        os.makedirs(code_dir)

    CODE_DIR = code_dir
    USR_DIR = usr_dir
    PACKAGES_FILE = packages_file

    with open(packages_file, "r") as config_file:
        CONFIG = json.load(config_file)


def main():

    parser = get_arg_parser()
    args = parser.parse_args()
    opt = configparser.ConfigParser()

    setup_config_files(args, opt)

    setup_logging(args, opt)

    if args.setup:
        logging.info("Setup for config files done.")
        raise SystemExit

    if args.command is None:
        parser.print_help()
        raise SystemExit

    commands = get_commands_map()

    ConfigurationAware.set_configuration(CONFIG, INSTALL_SCRIPTS_DIR, CACHE, opt)

    logging.debug("Code dir: %s", CODE_DIR)
    logging.debug("Usr dir: %s", USR_DIR)
    logging.debug("Packages file: %s", PACKAGES_FILE)
    logging.debug("Install script directory: %s", INSTALL_SCRIPTS_DIR)
    logging.debug("Cache file: %s", CACHE)

    core_manager = Manager()

    commands[args.command](args, core_manager)


if __name__ == "__main__":
    main()
