#!/usr/bin/python


import os, sys, argparse, json
import subprocess
from utils import Installer
from utils import flatten 
import configparser







install_cache = list()
inst = None

def install_package(name, config, directory, reinstall=False):
    global install_cache
    package = config["packages"][name]

    #Check dependencies
    install_cache.append(name)
    if "dependencies" in package:
        for dep in package["dependencies"]:
           if dep in install_cache:
               print("Thers is a cirlucar dependency between packages. This is not allowed!")
               print(f"{name} depends on {dep} and the other way around.")
               exit(1)
           else:
               print(f"Dependency: {name} -> {dep}")
               install_package(dep, config, directory, reinstall=reinstall)
    install_cache.remove(name)

    
    print(f"Installing {name}")
    
    last_edit = os.curdir
    package_dir = os.path.join(directory, name)

    if not os.path.isdir(package_dir):
        if reinstall:
            print(f"Reinstalling {name} but there is no directory. Install first!")
            exit(1)
        os.makedirs(package_dir)
    
    if len(os.listdir(package_dir)) != 0 and reinstall == False:
        print(f"The direcory ({package_dir}) is not empty and the package (name) is not in cache")
        print("Deleting direcotry\'s contents")
        os.system(f"rm -rf {package_dir}/* {package_dir}/.* 2> /dev/null")

    os.chdir(package_dir)
    
    if not reinstall:
        print(f"Downloading {name}")
        if package["download"] == "git":
            print(f"Using git and cloning from {package['URL']}")
            print(f"Cloning into {os.path.abspath('.')}")
            url = package['URL']
            os.system(f"git clone -q {url} .")
        elif package["download"] == "curl":
            print(f"Using curl and downloading from {package['URL']}")
            print(f"Downloading into {os.path.abspath(package_dir)}")
            os.system(f"curl -LOs {package['URL']} .")
        elif package["download"] == "wget":
            print(f"Using wget and downloading from {package['URL']}")
            print(f"Downloading into {os.path.abspath(package_dir)}")
            os.system(f"wget -q {package['URL']} .")
        

    res = inst.install(name, package, reinstall=False)
    if res != 0:
        print(f"Package {name} could not be installed")
        exit(1)
    
    os.chdir(last_edit)

    
    print("##############################")


def install(config, directory, packages):
    if packages is None:
        return
    flat = flatten(config["packages_list"])
    for pack in packages:
        if pack not in flat:
            print(f"Package {pack} is not in the config file")
        else:
            install_package(pack, config, directory)

            
def reinstall(config, directory, packages):
    if packages is None:
        return
    flat = flatten(config["packages_list"])
    for pack in packages:
        if pack not in flat:
            print(f"Package {pack} is not in the config file")
        else:
            install_package(pack, config, directory, reinstall=True)

            
def install_all(config, directory,group=None):
    packages = config["packages_list"]
    if group is not None and group > 0 and group < len(packages):
        packages = packages[group]
    print(f"Installing: {packages}")
    
    install(config, directory, packages)

def reinstall_all(config, directory,group=None):
    packages = config["packages_list"]
    if group is not None and group > 0 and group < len(packages):
        packages = packages[group]
    print(f"Installing: {packages}")
    
    reinstall(config, directory, packages)


def main():
    parser = argparse.ArgumentParser(description='Installs system packages from the INTERNET!!')

    parser.add_argument('--install', dest='packages',
                        help='Packages to install', nargs='+')

    parser.add_argument('--reinstall', dest='reinstall',
                        help='Packages to reinstall', nargs='+')
    
    parser.add_argument('--code-dir', dest='code_dir', action='store', required=False,
                        help='A folder to put the source of the packages')

    parser.add_argument('--usr-dir', dest='usr_dir', action='store', required=False,
                        help='A folder to install the packages')

    parser.add_argument('--packages-file', dest='packages_file', action='store',
                        help='File to read the packages from')

    parser.add_argument('--install-all', dest='all', action='store', type=int,
                        help='Install all packages in --packages from the given group')
    parser.add_argument('--reinstall-all', dest='reall', action='store', type=int,
                        help='Reinstall all packages in --packages from the given group')

    parser.add_argument('--no-install', dest='noinstall', action='store_true', default=False,
                        help='If present, packages will only be downloaded')

    args = parser.parse_args()    
    opt = configparser.ConfigParser()


    script_dir = os.path.dirname(os.path.abspath(__file__))

    
    opt.read(os.path.join(script_dir,'conf'))

    packages_file = opt["Set"]["packages_file"]
    code_dir = opt["Set"]["code"]
    usr_dir = opt["Set"]["usr"]

    
    
    code_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(code_dir)))
    usr_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(usr_dir)))
    packages_file = os.path.abspath(os.path.expanduser(os.path.expandvars(packages_file)))
    
    code_dir = os.path.abspath(os.path.expanduser(args.code_dir)) if args.code_dir is not None else code_dir
    usr_dir = os.path.abspath(os.path.expanduser(args.usr_dir)) if args.usr_dir is not None else usr_dir
    packages_file = os.path.abspath(os.path.expanduser(args.packages_file)) if args.packages_file is not None else packages_file

    
    config = None
    with open(os.path.join(script_dir, packages_file)) as config_file:
        config = json.load(config_file)

    if not os.path.isdir(code_dir):
        os.makedirs(code_dir)

    if not os.path.isdir(usr_dir):
        os.makedirs(usr_dir)

    global inst
    inst = Installer(usr_dir, args.noinstall)
    
    if args.all is not None:
        install_all(config, code_dir, group=args.all)
    elif args.reall is not None:
        reinstall_all(config, code_dir, group=args.reall)
    else:
        install(config, code_dir, args.packages)
        reinstall(config, code_dir, args.reinstall)



if __name__ == '__main__':
    main()
