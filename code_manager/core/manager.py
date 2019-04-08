from code_manager.core.installation import Installation
from code_manager.core.fetcher import Fetcher
from code_manager.core.configuration import ConfigurationAware
# from code_manager.core.deb_dependency import Depender
from code_manager.core.cache_container import CacheContainer

from code_manager.utils.utils import flatten


class Manager(ConfigurationAware):

    install = False
    build = False
    fetch = False

    def __init__(self):

        self.install_queue = list()

        # self.deb_dep = Depender()

        self.installation = Installation()
        self.cache = CacheContainer()
        self.fetch = Fetcher()

        if self.debug:
            self._setup_all()

    # def _fix_git_status(self, name, package):
    #     if "branch" in package.keys():
    #         os.system(f"git checkout {package['branch']}")
    #     if "commit" in package.keys():
    #         os.system(f"git checkout {package['commit']}")
    #     elif "tag" in package.keys():
    #         os.system(f"git checkout tags/{package['tag']}")

    # def _install_package(self, name, reinstall=False):
        # package = self.config["packages"][name]
        # # Check dependencies
        # self._check_dependencies(name, package, self.directory, reinstall)

        # # ckeck cache
        # cached = self._check_cache(name)
        # if cached:
        #     print(f"{name} is already installed (it\'s in the cache).")
        #     return 0

        # print(f"Installing \'{name}\'.")

        # last_edit = os.curdir
        # package_dir = os.path.join("direcory", name)
        # if not os.path.isdir(package_dir):
        #     if reinstall:
        #         print(f"Reinstalling {name} but there is\
        #         no directory. Install first!")
        #         exit(1)
        #     os.makedirs(package_dir)

        # if (os.listdir(package_dir)
        #     and reinstall is False and self.force_clear):
        #     print(f"The direcory ({package_dir}) is not empty\
        #     and the package (name) is not in cache")
        #     print("Delete the direcotry\'s contents first")
        #     exit(1)

        # os.chdir(package_dir)

        # if ("commit" in package.keys() or "branch" in package.keys()
        #         or "tag" in package.keys()):
        #     self._fix_git_status(name, package)

        # if not reinstall or os.listdir(package_dir):
        #     print(f"Downloading {name} in {package_dir}")
        #     self.down.download(name, self.config)

        # # resolve dependencies
        # if "deb_packages" in package.keys():
        #     print("Resolving Debian packages dependencies")
        #     self.deb_dep.install_deb_packages(package["deb_packages"])

        # res = self.inst.install(name, package, reinstall=False)

        # if res != 0:
        #     print(f"Package {name} could not be installed")
        #     exit(1)

        # os.chdir(last_edit)
        # with open(self.cache_file, "a") as cache:
        #     cache.write(name + "\n")

        # print("##############################")
        # return None

    def _setup_all(self):

        self.installation.load_installer()

    def _invoke(self):
        pass

    def fetch_package(self, package):
        self.fetch.download(package, package)

    def _install_thing(self, thing):

        if thing in self.packages_list.keys():
            print(r'\`{0}\` is a group. Installing all packages in it.'
                  .format(thing))
            self.install_queue = (self.install_queue
                                  + self.config["packages_list"][thing])

        elif thing in flatten(self.packages_list.values()):
            print(r'\`{0}\` is a package. Installing it.'.format(thing))
            self.install_queue.append(thing)

        else:
            print('There is no thing with name {0}'.format(thing))

    def install_thing(self, thing, install=True, fetch=False, build=False):
        if install:
            self.install = True
            self.fetch = True
            self.build = True
        elif build:
            self.install = False
            self.fetch = True
            self.build = True
        elif fetch:
            self.install = False
            self.build = False
            self.fetch = True

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
