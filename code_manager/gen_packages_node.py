#!/usr/bin/env python
import argparse
import json
import re

GIT_REGI = [
    re.compile(r'.*github\.com.*'),
    re.compile(r'.*gitlab\.com.*'),
    re.compile(r'.*bitbucket\.org.*'),
    re.compile(r'.*bitbucket\.org.*'),
    re.compile(r'.*git\..*'),
]


def is_git_url(fetch):
    for reg in GIT_REGI:
        if reg.match(fetch):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        prog='gen-packages-node', description='Quickly generate a package node for the packages.json file of code-manager.',
    )

    parser.add_argument('name', help='Name of the package.')
    parser.add_argument('fetch', default=None, nargs='?', help='URL to fetch the package from.')
    parser.add_argument('-g', '--git', default=False, action='store_true', help='Signify that the fetch url is git url.')

    parser.add_argument('-m', '--make', default=False, action='store_true', help='Signify usage of the make installer.')
    parser.add_argument('-c', '--cmake', default=False, action='store_true', help='Signify usage of the cmake installer.')

    args = parser.parse_args()

    node_dict = {}
    node_dict[args.name] = {}

    if args.fetch is not None:
        if is_git_url(args.fetch) or args.git:
            node_dict[args.name]['fetch'] = 'git'
            node_dict[args.name]['git'] = {}
            node_dict[args.name]['git']['url'] = args.fetch

    if args.cmake:
        node_dict[args.name].setdefault('install', [])
        node_dict[args.name]['install'].append('cmake')

    if args.make:
        node_dict[args.name].setdefault('install', [])
        node_dict[args.name]['install'].append('make')

    print(f'"{args.name}" : ' + json.dumps(node_dict[args.name], indent=4, separators=(',', ' : ')) + ',')


if __name__ == '__main__':
    main()
