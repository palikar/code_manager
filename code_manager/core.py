
import os, sys, argparse, json
import subprocess, configparser


from code_manager.installer import Installer
from code_manager.downloader import Downloader
from code_manager.deb_dependency import Depender
from code_manager.utils import flatten 




class Core:


    def __init__(self, noinstall, cache_file, config, code_dir, usr_dir, install_scripts_dir):
        self.install_cache = list()
        self.inst = Installer(usr_dir, install_scripts_dir,  noinstall=noinstall)
        self.down = Downloader()
        self.deb_dep = Depender()
        self.config = config
        self.install_scripts_dir = install_scripts_dir
        self.cache_file = cache_file


        

    def _install_package(self, name, config, directory, reinstall=False):
        package = config["packages"][name]

        #Check dependencies
        self.install_cache.append(name)
        if "dependencies" in package:
            for dep in package["dependencies"]:
               if dep in install_cache:
                   print("Thers is a cirlucar dependency between packages. This is not allowed!")
                   print(f"{name} depends on {dep} and the other way around.")
                   exit(1)
               else:
                   print(f"Dependency: {name} -> {dep}")
                   self._install_package(dep, config, directory, reinstall=reinstall)
        self.install_cache.remove(name)

        # ckeck cache
        cached = False
        with open(self.cache_file, "r") as cache:
            if name in cache.read().splitlines():
                cached = True

        if cached:
            print(f"{name} is already installed (it\'s in the cache).")
            return 0


        print(f"Installing \'{name}\'.")

        last_edit = os.curdir
        package_dir = os.path.join(directory, name)

        if not os.path.isdir(package_dir):
            if reinstall:
                print(f"Reinstalling {name} but there is no directory. Install first!")
                exit(1)
            os.makedirs(package_dir)

        if len(os.listdir(package_dir)) != 0 and reinstall == False:
            print(f"The direcory ({package_dir}) is not empty and the package (name) is not in cache")
            print("Delete the direcotry\'s contents first")
            exit(1)
            # os.system(f"rm -rf {package_dir}/* {package_dir}/.* 2> /dev/null")

        os.chdir(package_dir)

        if not reinstall:
            print(f"Downloading {name} in {package_dir}")
            self.down.download(name, config)


        #resolve dependencies
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



    def install(self, config, directory, packages, reinstall=False):
        if packages is None:
            return
        packages = flatten(packages)
        flat = flatten(config["packages_list"])
        for pack in packages:
            if pack not in flat:
                print(f"Package {pack} is not in the config file!")
                exit(1)
            else: 
                self._install_package(pack, config, directory, reinstall=reinstall)


    def install_all(self, config, directory,group=None, reinstall=False):
        packages = config["packages_list"]
        if group is not None and group > 0 and group < len(packages):
            packages = packages[group]
        print(f"Installing: {packages}")

        install(config, directory, packages, reinstall=reinstall)


