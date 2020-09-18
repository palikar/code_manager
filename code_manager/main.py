#!/usr/bin/env python
import argparse
import configparser
import contextlib
import json
import locale
import logging
import os
import subprocess
import sys
import tempfile
from shutil import copyfile
from shutil import copytree

import termtables

import code_manager
from code_manager.core.configuration import ConfigurationAware
from code_manager.core.manager import Manager
from code_manager.utils.logger import setup_logging
from code_manager.utils.printing import less
from code_manager.utils.read_input import promt
from code_manager.utils.read_input import promt_yes_no
from code_manager.utils.setenv import get_default_setenv
from code_manager.utils.utils import flatten
from code_manager.utils.utils import is_venv
from code_manager.utils.utils import sanitize_input_variable
from code_manager.utils.utils import venv
from code_manager.version import VERSION


VERSION_MSG = [
    f'code-manager version: {VERSION}',
    'Python version: {}'.format(
        ' '.join(line.strip() for line in sys.version.splitlines()),
    ),
    'Locale: {}'.format('.'.join(str(s) for s in locale.getlocale())),
]

# pylint: disable=W0603
COMMANDS = dict()


def command(name):
    global COMMANDS

    def inner(func):
        COMMANDS[name] = func
        return func
    return inner


def get_arg_parser():

    parser = argparse.ArgumentParser(
        prog='code-mananger', description='Installs system packages from the INTERNET!!',
    )

    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=('\n'.join(VERSION_MSG)),
        help='Print veriosn inormation',
    )

    parser.add_argument(
        '--code-dir',
        dest='code_dir',
        action='store',
        required=False,
        help='A folder to put the source of the packages',
    )

    parser.add_argument(
        '--usr-dir',
        dest='usr_dir',
        action='store',
        required=False,
        help='A folder to install the packages',
    )

    parser.add_argument(
        '--packages-file',
        '-p',
        dest='package',
        action='append',
        default=[],
        help='packages.json files to load packages from.',
    )

    parser.add_argument(
        '--setup-only',
        dest='setup',
        action='store_true',
        default=False,
        help='Only copy the config files if needed',
    )

    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        default=False,
        help='Run in debug mode outputing more information',
    )

    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Print a lot of information about the execution.',
    )

    subparsers = parser.add_subparsers(
        title='Commands',
        description='A list\
        of available commands',
        dest='command',
        metavar='Command',
    )

    parser_install = subparsers.add_parser(
        'install',
        description='Full installatio \
        of packages',
        help='Installs packages \
        (fetch, build and install)',
    )

    parser_install.add_argument(
        'packages', nargs='*', default=None, help='A list of packages to install',
    )

    parser_install.add_argument(
        '--reinstall',
        dest='reinstall',
        action='store_true',
        help='Should the packages be reinstalled',
    )

    parser_install.add_argument(
        '--group',
        action='store',
        metavar='group',
        default=None,
        help='Should the packages be reinstalled',
    )

    parser_install.add_argument(
        '-n',
        '--no-apt',
        action='store_false',
        dest='apt',
        default=True,
        help='If given, don\'t install apt packages automaticall but give a command to be executed.',
    )

    parser_fetch = subparsers.add_parser(
        'fetch',
        description='Downloads packages but\
        it does not install them nor builds\
        them. If a name of a group is given,\
        all packages of the group will\
        be downloaded.',
        help='Downloads packages',
    )

    parser_fetch.add_argument(
        'packages', nargs='*', default=None, help='A list of packages to fetch',
    )

    parser_fetch.add_argument(
        '-f', '--force', default=False, dest='force',
        action='store_true', help='Will delete anyfolders that stay on its way',
    )

    parser_fetch.add_argument(
        '--group',
        action='store',
        metavar='name',
        default=None,
        help='If given, every\
        package from this group will be fetched',
    )

    parser_build = subparsers.add_parser(
        'build',
        description='Builds a package\
        from source',
        help='Builds the project of package',
    )
    parser_build.add_argument(
        'packages', nargs='*', default=None, help='A list of packages to build.',
    )
    parser_build.add_argument(
        '--group',
        action='store',
        metavar='name',
        default=None,
        help='If given, every package\
        from this group will be build',
    )
    parser_build.add_argument(
        '--no-install',
        dest='noinstall',
        action='store_true',
        default=False,
        help='If present, packages will only be build but not installed.',
    )

    parser_remove = subparsers.add_parser(
        'remove',
        description='Remove a package',
        help='Remove a package and its sources',
    )

    parser_remove.add_argument(
        'packages', nargs='*', default=None, help='A list of packages to remove.',
    )

    list_packages_parser = subparsers.add_parser(
        'list-packages',
        description='Lists the installed packages',
        help='Lists the installed packages.',
    )

    list_packages_parser.add_argument(
        '--no-pager',
        action='store_true',
        dest='no_pager',
        default=False,
        help='Disable the pager while printing the packeges.',
    )

    subparsers.add_parser(
        'list-fetchers',
        description='Lists the available fetchers',
        help='Lists fetchers.',
    )

    list_cache_parser = subparsers.add_parser(
        'list-cache',
        help='Show the entries in the cache',
    )

    list_cache_parser.add_argument(
        'packages',
        action='store',
        default=None,
        nargs='*',
        help='if given, print information about specific\
packege in the cache',
    )

    list_cache_parser.add_argument(
        '-p',
        '--plain',
        action='store_true',
        default=False,
        help='Print the the packages in cache in\
a simple, one line manner',
    )

    list_cache_parser.add_argument(
        '--skip-header',
        action='store_true',
        dest='skip_header',
        default=False,
        help="Don't print the first line when printing packages with --plain",
    )

    list_cache_parser.add_argument(
        '--no-pager',
        action='store_true',
        dest='no_pager',
        default=False,
        help='Disable the pager while printing the packeges in a table form.',
    )

    clear_parser = subparsers.add_parser(
        'clear-cache', help='Clears the entries in the cache file',
    )

    clear_parser.add_argument(
        'packages', nargs='*', default=None, help='A list of packages to remove from cache.',
    )

    edit_parser = subparsers.add_parser(
        'edit-cache', help='Edit the cache file',
    )

    edit_parser.add_argument(
        'package', nargs='?', default=None, help='Package for which to edit the cahce file.',
    )

    clear_parser.add_argument(
        '-a', '--all', dest='all', action='store_true',
        default=False, help='Clear the enitrety of the cache file.',
    )

    rebuild_parser = subparsers.add_parser(
        'rebuild-cache', help='Rebuild the main cache file from the per-package ones',
    )

    rebuild_parser.add_argument(
        '--assume-installed', dest='assume_installed', action='store_true',
        default=False, help='Assume all folders in the code directory have a valid installed project.',
    )

    groups_parser = subparsers.add_parser(
        'list-groups', help='List the avaialble groups or the packeges in them',
    )
    groups_parser.add_argument(
        'groups',
        action='store',
        default=None,
        nargs='*',
        help='Groups to list. Will list every group if not given',
    )

    grep_parser = subparsers.add_parser(
        'grep', help='Distributed grep over the fetched pakcages',
    )
    grep_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    grep_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    grep_parser.add_argument(
        'rest', nargs=argparse.REMAINDER, help='Arguments passed to the grep command',
    )

    sed_parser = subparsers.add_parser(
        'sed', help='Distributed sed over the fetched pakcages',
    )
    sed_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    sed_parser.add_argument(
        '-s', '--sed-args', action='append', default=[], dest='sed_args',
        help='Extra argument for the sed command.',
    )
    sed_parser.add_argument(
        '-i', '--in-place', action='store_true', default=False, dest='inplace',
        help='Run the sed command with the \'-i\' flag.',
    )
    sed_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    sed_parser.add_argument(
        'expression', action='store',
        help='Sed expression to use.',
    )
    sed_parser.add_argument(
        'files', action='store',
        help='A glob for filenames.',
    )
    sed_parser.add_argument('rest', nargs=argparse.REMAINDER)

    push_parser = subparsers.add_parser(
        'push', help='Push every pacakge with git repo',
    )
    push_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    push_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    push_parser.add_argument('rest', nargs=argparse.REMAINDER)

    pull_parser = subparsers.add_parser(
        'pull', help='Pull every pacakge with git repo',
    )
    pull_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    pull_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    pull_parser.add_argument('rest', nargs=argparse.REMAINDER)

    commit_parser = subparsers.add_parser(
        'commit', help='Make commit for every pacakge with git repo',
    )
    commit_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    commit_parser.add_argument(
        'message', action='store',
        help='Message for the newly created commit.',
    )
    commit_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    commit_parser.add_argument('rest', nargs=argparse.REMAINDER)

    find_parser = subparsers.add_parser(
        'find', help='Run distributed find command for every package.',
    )
    find_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    find_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    find_parser.add_argument(
        'files', action='store',
        help='A glob for filenames.',
    )
    find_parser.add_argument('rest', nargs=argparse.REMAINDER)

    root_parser = subparsers.add_parser(
        'root', help='Find the root directory of package',
    )
    root_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    root_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    root_parser.add_argument('rest', nargs=argparse.REMAINDER)

    command_parser = subparsers.add_parser(
        'command', help='Execute general shell command\
 in the root directory of a package.',
    )
    command_parser.add_argument(
        '-t', '--thing', action='store', default=None, dest='thing',
        help='Group or package to execute the command for.',
    )
    command_parser.add_argument(
        '-n', '--no-color', action='store_true', default=None, dest='no_color',
        help='Supress any color in the output',
    )
    command_parser.add_argument(
        '-g', '--git-only', action='store_true', default=None, dest='git',
        help='Execute the command only for git repositories.',
    )
    command_parser.add_argument(
        'rest', nargs=argparse.REMAINDER, help='The command to execute.',
    )

    return parser


@command('install')
def install(args, core):
    if args.group is not None:
        core.install_thing(args.group, install=True)
    else:
        core.install_thing(args.packages, install=True)


@command('fetch')
def fetch(args, core):
    if args.group is not None:
        core.install_thing(args.group, fetch=True, force=args.force)
    else:
        core.install_thing(args.packages, fetch=True, force=args.force)


@command('build')
def build(args, core):
    if args.group is not None:
        core.install_thing(args.group, build=True)
    else:
        core.install_thing(args.packages, build=True)


@command('remove')
def remove(args, core):
    core.remove_package(args.packages)


@command('list-packages')
def list_packages(args, core):
    logging.debug('Available packages:')
    packs = flatten(core.packages_list.values())
    if len(packs) > 10 and not args.no_pager:
        less(bytes('\n'.join(packs), 'utf-8'))
        return
    print('\n'.join(packs))


@command('list-cache')
def list_cache(args, core):
    logging.debug('Dumping cache file %s', core.cache_file)

    cache = core.get_cache_content()
    header = ['Name', 'Fetched', 'Built', 'Installed', 'Root']
    rows = list(map(lambda x: list(x.values()), cache))

    if args.packages:
        rows = list(filter(lambda x: x[0] in args.packages, rows))

    if args.plain:
        for values in rows:
            line = ','.join(str(val) for val in values)
            print(line)
    else:
        string = termtables.to_string(
            rows,
            header=header,
            style=termtables.styles.ascii_thin_double,
            padding=(0, 1),
            alignment='lcccc',
        )
        if len(string.split('\n')) > 10 and not args.no_pager:
            less(bytes(string, 'utf-8'))
        else:
            print(string)


@command('list-groups')
def list_groups(args, core):

    if not args.groups:
        groups = core.get_groups()
        string = '\n'.join(groups)
        print(string)
    else:
        for group in args.groups:
            packs = core.get_group_packages(group)
            string = '\n'.join(packs)
            print(string)


@command('clear-cache')
def clear_cache(args, core):

    if args.all:
        logging.info('Clearing cache file %s', core.cache_file)
        if promt_yes_no('Are you sure you want to clear the cache?'):
            handle = open(core.cache_file, 'w')
            handle.close()
    if args.packages is not None:
        for pack in args.packages:
            logging.info('Removing %s from the cache file %s', pack, core.cache_file)
            with core.get_cache() as cache:
                cache.drop(pack)


@command('edit-cache')
def edit_cache(args, core):
    if args.package is None:
        logging.info('Editing %s', core.cache_file)
        os.system('{} {}'.format(os.getenv('EDITOR'), core.cache_file))
    else:
        pack = args.package
        logging.info('Editing cache entry for %s', pack)

        with open(core.cache_file) as file_desc:
            cont = json.load(file_desc)

        _, filename = tempfile.mkstemp()
        with open(filename, 'w') as file_desc:
            json.dump(cont[pack], file_desc, indent=4)

        os.system('{} {}'.format(os.getenv('EDITOR'), filename))

        with open(filename) as file_desc:
            new_entry = json.load(file_desc)
        cont[pack] = new_entry

        with open(core.cache_file, 'w') as file_desc:
            json.dump(cont, file_desc, indent=4)


@command('rebuild-cache')
def rebuild_cache(args, core):
    core.rebuild_cache(args.assume_installed)


@command('grep')
def grep(args, core):
    core.run_command('grep', args, thing=args.thing)


@command('sed')
def sed(args, core):
    core.run_command('sed', args, thing=args.thing)


@command('push')
def push(args, core):
    core.run_command('push', args, thing=args.thing)


@command('pull')
def pull(args, core):
    core.run_command('pull', args, thing=args.thing)


@command('commit')
def commit(args, core):
    core.run_command('commit', args, thing=args.thing)


@command('find')
def find(args, core):
    core.run_command('find', args, thing=args.thing)


@command('root')
def root(args, core):
    core.run_command('root', args, thing=args.thing)


@command('command')
def execture(args, core):
    core.run_command('command', args, thing=args.thing)


@command('list-fetchers')
def list_fetchers(_, core):
    print('Currently available fetchers:')
    for fetcher in core.get_fetchers():
        print(f'\t - {fetcher}')


def copy_config():

    private_data_dir = os.path.join(code_manager.CMDIR, 'data')

    with contextlib.suppress(FileExistsError):
        os.mkdir(code_manager.CONFDIR)

    if not os.path.isfile(os.path.join(code_manager.CONFDIR, 'packages.json')):
        copyfile(
            os.path.join(private_data_dir, 'packages.json'),
            os.path.join(code_manager.CONFDIR, 'packages.json'),
        )

    if not os.path.isfile(os.path.join(code_manager.CONFDIR, 'conf')):
        copyfile(
            os.path.join(private_data_dir, 'conf'),
            os.path.join(code_manager.CONFDIR, 'conf'),
        )

    if not os.path.isdir(os.path.join(code_manager.CONFDIR, 'install_scripts')):
        copytree(
            os.path.join(code_manager.CMDIR, 'install_scripts'),
            os.path.join(code_manager.CONFDIR, 'install_scripts'),
        )

    if not os.path.isfile(os.path.join(code_manager.CONFDIR, 'sources')):
        copyfile(
            os.path.join(private_data_dir, 'sources'),
            os.path.join(code_manager.CONFDIR, 'sources'),
        )


def venv_check(opt):
    if is_venv():
        env = venv()
        cm_env = sanitize_input_variable(opt['Config']['venv'])
        if env != cm_env:
            logging.info("The activated virtual environment is not the one of code manageger.\
You have to source the 'setenv.sh' fist.")
            raise SystemExit
    else:
        logging.info(
            "No virtual environment is active. You have to source the 'setenv.sh' fist.",
        )
        raise SystemExit


def venv_setup(opt):

    python_ver = promt('Python executable', 'python3')
    env_root = promt(
        'Virtual environment location',
        sanitize_input_variable(opt['Config']['venv']),
    )
    opt['Config']['venv'] = env_root

    with contextlib.suppress(FileExistsError):
        os.makedirs(os.path.abspath(os.path.join(env_root, os.pardir)))

    logging.info('Python version: %s', python_ver)
    logging.info('VEnv root:%s', env_root)

    venv_command = [
        'virtualenv',
        '--system-site-packages',
        '-p', python_ver,
        env_root,
    ]

    logging.info('Creating a virtual environment for code_manager')
    logging.debug(' '.join(venv_command))
    subprocess.Popen(venv_command).wait()

    with open(os.path.join(opt['Config']['code'], 'setenv.sh'), 'w') as file_handle:
        file_handle.write(get_default_setenv(opt))

    logging.info('The environment is now ready. You should source the\
\'setenv.sh\' file to use code_manager')


def dir_setup(opt):
    opt['Config']['code'] = promt(
        'Code direcotry:', sanitize_input_variable(opt['Config']['code']),
    ).strip()
    opt['Config']['usr'] = promt(
        'Usr direcotry:', sanitize_input_variable(opt['Config']['usr']),
    ).strip()

    with contextlib.suppress(FileExistsError):
        os.makedirs(opt['Config']['code'])
    with contextlib.suppress(FileExistsError):
        os.makedirs(opt['Config']['usr'])


def save_opt(opt):
    with open(os.path.join(os.path.join(code_manager.CONFDIR, 'conf')), 'w') as configfile:
        opt.write(configfile)


def main():

    parser = get_arg_parser()
    args, _ = parser.parse_known_args()
    opt = configparser.ConfigParser()

    if hasattr(args, 'rest') and '--' in args.rest:
        args.rest.remove('--')

    copy_config()
    opt.read(os.path.join(code_manager.CONFDIR, 'conf'))
    setup_logging(args, opt)

    if args.setup:
        logging.info('Setting up direcories and file for code_manger.')
        dir_setup(opt)
        venv_setup(opt)
        save_opt(opt)
        raise SystemExit

    venv_check(opt)

    if args.command is None:
        parser.print_help()
        raise SystemExit

    ConfigurationAware.set_configuration(opt, args)

    core_manager = Manager()

    COMMANDS[args.command](args, core_manager)

    raise SystemExit


if __name__ == '__main__':
    main()
