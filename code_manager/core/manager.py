import os
import json

from code_manager.core.installer import Installer
from code_manager.core.downloader import Downloader
from code_manager.core.configuration import ConfigurationAware
from code_manager.core.deb_dependency import Depender
from code_manager.core.cache_container import CacheContainer

from code_manager.utils.utils import flatten


class Manager(ConfigurationAware):



    def __init__(self):

        self.install_queue = list()

        self.inst = Installer(self.usr_dir, self.install_scripts_dir,
                              noinstall=False)

        self.down = Downloader()
        self.deb_dep = Depender()
        self.cache = CacheContainer()




    def _fix_git_status(self, name, package):
        if "branch" in package.keys():
            os.system(f"git checkout {package['branch']}")
        if "commit" in package.keys():
            os.system(f"git checkout {package['commit']}")
        elif "tag" in package.keys():
            os.system(f"git checkout tags/{package['tag']}")
        pass


    def _install_package(self, name, reinstall=False):
        package = self.config["packages"][name]

        # Check dependencies
        self._check_dependencies(name, package, self.directory, reinstall)

        # ckeck cache
        cached = self._check_cache(name)
        if cached:
            print(f"{name} is already installed (it\'s in the cache).")
            return 0

        print(f"Installing \'{name}\'.")

        last_edit = os.curdir
        package_dir = os.path.join(directory, name)
        if not os.path.isdir(package_dir):
            if reinstall:
                print(f"Reinstalling {name} but there is\
                no directory. Install first!")
                exit(1)
            os.makedirs(package_dir)

        if (len(os.listdir(package_dir)) != 0 and reinstall is False and self.force_clear):
            print(f"The direcory ({package_dir}) is not empty\
            and the package (name) is not in cache")
            print("Delete the direcotry\'s contents first")
            exit(1)

        os.chdir(package_dir)

        if ("commit" in package.keys() or "branch" in package.keys()
            or "tag" in package.keys()):
            self._fix_git_status(name, package)

        if not reinstall or len(os.listdir(package_dir)) == 0:
            print(f"Downloading {name} in {package_dir}")
            self.down.download(name, config)

        # resolve dependencies
        if "deb_packages" in package.keys():
            print("Resolving Debian packages dependencies")
            self.deb_dep.install_deb_packages(package["deb_packages"])

        res = self.inst.install(name, package, reinstall=False)

        if res != 0:
            print(f"Package {name} could not be installed")
            exit(1)

        os.chdir(last_edit)
        with open(self.cache_file, "a") as cache:
            cache.write(name + "\n")

        print("##############################")
        return res


    def _invoke(self):

        self.install_order = []
        all_packages = flatten(self.config["packages_list"].values())
        deps = []

        for p in self.install_queue:

            if p in self.install_order:
                continue

            new_packages = []

            if 'dependencies' is self.config['packages'][p].keys():
                new_packages = new_packages + self.config['packages'][p]['dependencies']

            deps = deps + new_packages

            self.install_order = new_packages + [p] + self.install_order




    def _install_thing(self, thing):

        if thing is self.packages_list().keys():
            print('\`%s\` is a group. Installing all packages in it.'.format(thing))
            self.install_queue = self.install_queue + self.config["packages_list"][thing]

        elif thing is flatten(self.packages_list().values()):
            print('\`%s\` is a package. Installing it.'.format(thing))
            self.install_queue.append(thing)

        else:
            print('There is no thing with name %s'.format(thing))
            return


    def install(self, thing, install=True, fetch=False, build=False):
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
            for t in thing:
                self._install_thing(t)
        else:
            self._install_thing(thing)

        self._invoke()
