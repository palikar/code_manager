import sys
import logging
import difflib

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.utils import flatten


class DebGrapher(ConfigurationAware):

    def __init__(self):
        logging.debug("Initializing the DepGrapher")

    def get_packages(self, group=""):  # pylint: disable=R1705
        if group == "":
            return flatten(self.packages_list.values())
        else:
            if group in self.packages_list.keys():
                return self.packages_list[group]  # pylint: disable=E1136
            else:
                logging.critical("There is no group\
                with the name %s.", group)
                return None

    def verify_package_list(self, package_names):
        all_packs = set(flatten(self.packages_list.values()))
        for pack in package_names:
            if pack not in all_packs:
                logging.info("The package %s is not\
in the list with packags.", pack)
                logging.info("Did you mean any of the following: %s",
                             ",".join(difflib.get_close_matches(pack, all_packs, 5)))
                sys.exit(1)
        return 0

    def verify_packages_tree(self):
        # TODO: Check if the builds are there
        # TODO: Check for circular dependencies
        all_packs_list = set(flatten(self.packages_list.values()))
        all_packs_nodes = set(self.packages.keys())  # pylint: disable=E1101

        broken = []
        # Every package is in a group
        for pack in all_packs_nodes:
            if pack not in all_packs_list:
                broken.append(pack)

        if broken:
            logging.critical("Inconsistent packages file!\
The packages [%s] are not in any group", ','.join(broken))
            sys.exit(1)

        broken = []
        # Every package in a group is in the nodes
        for pack in all_packs_list:
            if pack not in all_packs_nodes:
                broken.append(pack)

        if broken:
            logging.critical("Incosistant packages file!\
The packages [%s] do not have node", ','.join(broken))
            sys.exit(1)

        # Every dependency is in the packages.json
        for pack in all_packs_nodes:
            for deb in self.get_dependencies(pack):
                if deb not in all_packs_nodes:
                    logging.critical("%s is dependency\
of %s but it is not in the packages.json", deb, pack)
                    sys.exit(1)

    def get_dependencies(self, package):
        assert package is not None

        if package not in self.packages.keys():  # pylint: disable=E1101
            logging.critical("The package %s\
is not in the packages.json.", package)  # pylint: disable=E1136
            sys.exit(1)
        if 'dependencies' in self.packages[package].keys():
            return self.packages[package]['dependencies']  # pylint: disable=E1136
        else:
            return []

    def get_deep_dependencies(self, package):
        assert package is not None

        deps = set()
        packs_to_check = set(self.get_dependencies(package))
        while packs_to_check:
            dep = packs_to_check.pop()
            if dep not in deps:
                deps.add(dep)
                packs_to_check.update(self.get_dependencies(dep))
        return list(deps)

    def get_list_dependencies(self, packages):
        assert packages is not None

        deps = set()
        for pack in packages:
            deps.update(self.get_deep_dependencies(pack))
        return deps

    def get_build_order(self, packages):
        assert packages is not None

        sub_tree = {}
        for pack in sorted(packages):
            sub_tree[pack] = set()

        for pack in packages:
            for depend in self.get_dependencies(pack):
                if depend in sub_tree.keys():
                    sub_tree[pack].add(depend)

        build_order = []
        while sub_tree:
            available = [pack for pack, deps in sub_tree.items() if not deps]
            if not available:
                logging.critical('Build order cannot be generated.\
The packages tree is maybe broken.')
                sys.exit(1)
            for pack in available:
                build_order.append(pack)
                del sub_tree[pack]
            for pack, deps in sub_tree.items():
                deps -= set(available)

        return build_order
