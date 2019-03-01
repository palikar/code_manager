
import os
import json

from code_manager.installer import Installer
from code_manager.downloader import Downloader
from code_manager.deb_dependency import Depender
from code_manager.utils import flatten


class Core:

    def __init__(self, noinstall, cache_file, config, code_dir,
                 usr_dir, install_scripts_dir, force_clear):
        self.install_cache = list()
        self.inst = Installer(usr_dir, install_scripts_dir,
                              noinstall=noinstall)
        
        self.down = Downloader()
        self.deb_dep = Depender()
        self.config = config
        self.install_scripts_dir = install_scripts_dir
        self.cache_file = cache_file
        self.cache = None
        self.force_clear = force_clear



    def _get_package_group(self, package):
        
        return ""
            
        
    def _check_dependencies(self, name, package, directory, reinstall):

        self.install_cache.append(name)
        if "dependencies" in package:
            for dep in package["dependencies"]:
                if dep in self.install_cache:
                    print("Thers is a cirlucar dependency between packages.\
                    This is not allowed!")
                    print(f"{name} depends on {dep} and the other way around.")
                    exit(1)
                else:
                    print(f"Dependency: {name} -> {dep}")
                    self._install_package(dep,
                                          self.config,
                                          directory,
                                          reinstall=reinstall)
        self.install_cache.remove(name)

    def _preupdate_cache(self):

        # try:
        #     self.cache = json.load(open(self.cache_file, 'r'))
        # except ValueError ex:
        #     print('Invalid cache file!')
        #     print(e)
        #     exit(1)

        for package, node in config['packages'].items():
            if not package in self.cache:
                self.cache[package] = dict()
                self.cache[package]['node'] = node
                self.cache[package]['installed'] = False
                self.cache[package]['fetched'] = False
                self.cache[package]['built'] = False
                self.cache[package]['group'] = self._get_package_group(package)
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
                xno directory. Install first!")
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

    def install(self, packages, reinstall=False):
        if packages is None:
            return
        packages = flatten(packages)
        available_packages = flatten(self.config["packages_list"].values())

        for pack in packages:
            if pack not in available_packages:
                print(f"Package {pack} is not in the config file!")
            else:
                print(f'=====>Installing \'{pack}\' ')
                # self._install_package(pack,
                #                       reinstall=reinstall)
    def install_group(self, group, reinstall=False):
        if group is None:
            return

        if not group in self.config["packages_list"].keys():
            print(f'There is no group with name {group}')
            return 
            
        
        packages = flatten(self.config["packages_list"][group])
        
        for pack in packages:
            print(f'=====>Installing {pack}')
            # self._install_package(pack,
            #                       reinstall=reinstall)


    def get_installed_packages(self,group=None):
        #just look in the cache
        pass
        
