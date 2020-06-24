#!/usr/bin/env python

import argparse
import json

def main():
    parser = argparse.ArgumentParser(
        prog='gen-packages-node', description='Quickly generate a package node for the packages.json file of code-manager',
    )

    parser.add_argument('name', help='Name of the package')
    parser.add_argument('fetch', default=None, nargs='?', help='URL to fetch the package from.')

    args = parser.parse_args()

    node_dict = {}
    node_dict[args.name] = {}

    
    node_dict[args.name]['fetch'] = 'git'
    node_dict[args.name]['git'] = {}
    node_dict[args.name]['git']['url'] = args.fetch









    print(f'"{args.name}" : '+ json.dumps(node_dict[args.name], indent=4, separators=(',', ' : ')))

if __name__ == '__main__':
    main()
