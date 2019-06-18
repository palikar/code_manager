import logging

from code_manager.core.installation import Installation
from code_manager.core.fetcher import Fetcher
from code_manager.core.configuration import ConfigurationAware

# from code_manager.core.deb_dependency import Depender
from code_manager.core.cache_container import CacheContainer
from code_manager.utils.utils import flatten
from code_manager.utils.logger import debug_red


class Manager(ConfigurationAware):

    install = False
    build = False
    fetching = False

    def __init__(self):

        self.install_queue = list()

        # self.deb_dep = Depender()

        self.installation = Installation()
        self.cache = CacheContainer()
        self.fetcher = Fetcher()

        self._setup_all()

    def _setup_all(self):
        self.installation.load_installer()
        self.cache.load_cache()

    def _invoke(self):
        pass

    def fetch_package(self, package):
        with self.cache as cache:
            if cache.is_fetched(package):
                debug_red("The package '%s' is already fetched", package)
                return None
            if self.fetcher.download(package, package) is None:
                debug_red("The fetching of '%s' failed.", package)
                return None
            else:
                cache.set_fetched(package, True)
                cache.set_root(package, package)
            return 0

    def fetch_group(self, group):
        for pack in self.packages_list[group]:
            self.fetch_package(pack)

    def fetch_thing(self, thing):
        if thing in self.packages_list.keys():
            logging.info("'%s' is a group. Fetching all packages in it.", thing)
            self.fetch_group(thing)
        elif thing in flatten(self.packages_list.values()):
            logging.info("'%s' is a package. Fetching it.", thing)
            self.fetch_package(thing)
        else:
            logging.info("There is no thing with name '%s'", thing)

    def fetch(self, thing):
        if isinstance(thing, list):
            for thingy in thing:
                self.fetch_thing(thingy)
        elif isinstance(thing, str):
            self.fetch_thing(thing)
        else:
            logging.critical(
                "Can't install %s. It's \
            no string nor list",
                thing,
            )

    def _install_thing(self, thing):

        if thing in self.packages_list.keys():
            logging.debug(
                r"\`%s\` is a group. Installing all packages in it.", thing)
            self.install_queue = (
                self.install_queue + self.config["packages_list"][thing])

        elif thing in flatten(self.packages_list.values()):
            logging.debug(r"\`%s\` is a package. Installing it.", thing)
            self.install_queue.append(thing)

        else:
            logging.critical("There is no thing with name %s", thing)

    def install_thing(self, thing, install=True, fetch=False, build=False):
        if install:
            self.install = True
            self.fetching = True
            self.build = True
        elif build:
            self.install = False
            self.fetching = True
            self.build = True
        elif fetch:
            self.install = False
            self.fetching = True
            self.build = False

        if isinstance(thing, list):
            for name in thing:
                self._install_thing(name)
        else:
            self._install_thing(thing)

        if self.install_queue:
            self._setup_all()
            self._invoke()


# def generate_build_order(self, all_libs):
#        """
#        This function figures out the build order of an unordered list of libraries.
#        Tt does not add or remove anything make sure that the list is complete
#        """
#        merge_graph = {}
#        # set up the basic structure
#        for lib in sorted(all_libs):
#            base = self._depgraph[lib]['extends'] if 'extends' in self._depgraph[lib] else lib
#            merge_graph[base] = {'extends': set(), 'dependencies': set()}
#        # fill the structure
#        for lib in all_libs:
#            if 'extends' in self._depgraph[lib]:
#                base = self._depgraph[lib]['extends']
#                # if the lib is an extension add it to the parent
#                merge_graph[base]['extends'].add(lib)
#            else:
#                base = lib
#            # check the dependencies of the lib but add only those dependencies
#            # that are in our collected list of libraries all others are not
#            # relevant
#            for dep in self._get_dependencies(lib):
#                # if the dependency is an extension check with its root
#                root = self._depgraph[dep].get('extends', dep)
#                if root in merge_graph and root != base:
#                    merge_graph[base]['dependencies'].add(root)
#        logging.debug('simplified dep graph: %s', merge_graph)
#        # generate build build order
#        build_order = []
#        extends_dict = {}
#        while len(merge_graph) > 0:
#            # find all libraries without any unsatisfied dependencies
#            buildable = [depname for depname, data in merge_graph.items()
#                         if len(data['dependencies']) == 0]
#            if len(buildable) == 0:
#                logging.critical(
#                    'error could not generate build order. your dependency graph seems to be broken')
#                exit(-1)
#            # add the found libraries to the build order
#            for depname in buildable:
#                build_order.append(depname)
#                extends_dict[depname] = list(merge_graph[depname]['extends'])
#            # delete all processed libraries
#            for depname in buildable:
#                del merge_graph[depname]
#            # remove processed libraries from the dependencies of the remaining
#            # libraries
#            for key, dep in merge_graph.items():
#                dep['dependencies'] -= set(buildable)
#        logging.debug('build order %s with extends %s', build_order, extends_dict)
#        return build_order, extends_dict
