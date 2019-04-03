#!/usr/bin/python


import sys
import json
from code_manager.utils.utils import merge_two_dicts
from code_manager.utils.utils import flatten


def merge_package_file(input_files, output_file):
    new = dict()
    new["packages_list"] = list()
    new["debian_packages"] = list()
    new["packages"] = dict()
    for js in input_files:
        with open(js) as config_file:
            config = json.load(config_file)
            new["packages_list"].append(flatten(config["packages_list"]))
            new["debian_packages"].append(flatten(config["debian_packages"]))
            new["packages"] = merge_two_dicts(new["packages"],
                                              config["packages"])

    with open(output_file, 'w') as outfile:
        json.dump(new, outfile, indent=4,)


def main():
    merge_package_file(sys.argv[1:-1], sys.argv[-1])


if __name__ == '__main__':
    main()
