import os
import json

from code_manager.core.installer import Installer
from code_manager.core.downloader import Downloader
from code_manager.core.deb_dependency import Depender
from code_manager.utils.utils import flatten


class Manager:

    def __init__(self, noinstall, cache_file, config, code_dir,
                 usr_dir, install_scripts_dir, force_clear):

        self.install_queue = list()
        
        self.inst = Installer(usr_dir, install_scripts_dir,
                              noinstall=noinstall)

        self.down = Downloader()
        self.deb_dep = Depender()

        self.config = config
        self.install_scripts_dir = install_scripts_dir
        self.cache_file = cache_file
        self.cache = None
        self.force_clear = force_clear

        self._load_cache()
        self._preupdate_cache()


    def _load_cache(self):
         self.cache = json.load(open(self.cache_file, 'r'))

    def _preupdate_cache(self):
        for group, packages in self.config['packages_list'].items():
            for package in packages:
                if not package in self.cache:
                    self.cache[package] = dict()
                    self.cache[package]['node'] = node
                    self.cache[package]['installed'] = False
                    self.cache[package]['fetched'] = False
                    self.cache[package]['built'] = False
                    self.cache[package]['group'] = group
                    self.cache[package]['root'] = ""

        self._save_cache()

    def _save_cache(self):
        json.dump(self.cache, open(self.cache_file, 'w'))

    def _update_cache(self, name, package_node,
                      root,
                      build=False,
                      install=False,
                      fetched=False):
        self.cache[name]['node'] = package_node
        self.cache[name]['installed'] = installed
        self.cache[name]['fetched'] = fetched
        self.cache[name]['built'] = build
        self.cache[name]['root'] = root

        self._save_cache()

    def _check_cache(self, name, prop='installed'):
        return self.cache[name][prop]


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




    def _install_thing(self, thing):

        if thing is self.config["packages_list"].keys():
            print('\`%s\` is a group. Installing all packages in it.'.format(thing))
            self.install_queue = self.install_queue + self.config["packages_list"][thing]
        elif thing is flatten(self.config["packages_list"].values()):
            print('\`%s\` is a package. Installing it.'.format(thing))
            self.install_queue.append(thing)
        else:
            print('There is no thing with name %s'.format(thing))
            return

        self._invoke_install


    def install(self, thing, install=True, fetch=False, build=False):

        if isinstance(l, list):
            for t in thing:
                self._install_thing(t)
        else:
            self._install_thing(thing)

