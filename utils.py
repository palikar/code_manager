#!/usr/bin/python

import os, sys
import collections


def flatten(xs):
    res = []
    def loop(ys):
        for i in ys:
            if isinstance(i, list):
                loop(i)
            else:
                res.append(i)
    loop(xs)
    return res




    
class Installer:

    def __init__(self, usr_dir, noinstall=True):
        self.installers = dict()
        self.installers["script"] = self.install_with_script
        self.installers["command"] = self.install_with_command
        self.installers["cmake"] = self.install_with_cmake
        self.usr_dir = usr_dir
        self.noinstall = noinstall

        

    def install(self, name, package, reinstall=False):
        if self.noinstall:
            return 0
        if package["install"] not in self.installers.keys():
            print(f'Unknown installer {package["install"]} for package {name}')
            return -1
        else:
            return self.installers[package["install"]](name, package, reinstall=False)



    def install_with_script(self, name, package, reinstall=False):
        print(f"Installing {name} with script file")

        if "script" not in package:
            print("'script' field missing in the node form {name}")
            return -1
        script = package["script"]
        script = os.path.expanduser(script)
        script = os.path.expandvars(script)
        script = os.path.abspath(script)
        print(f"Used script: {script}")
        cmd_args = package["script_args"] if "script_args" in package else ""
        cmd_args = os.path.expanduser(cmd_args)
        cmd_args = os.path.expandvars(cmd_args)
        cmd_args = cmd_args + (" -r" if reinstall else "")
        cmd_args = cmd_args + f"-p {self.usr_dir}"
        print(f'Command: sh {script} {cmd_args}')
        # os.system(f'sh {script} ' + cmd_args)




    def install_with_command(self, name, package, reinstall=False):
        print(f"Installing {name} with command")
        #Make checks!
        if "command" not in package:
            print("'command' field missing in the node form {name}")
            return -1
        command = package["command"] if reinstall == False else package["reinstall_command"]
        command = os.path.expanduser(command)
        command = os.path.expandvars(command)
        print(f"Command: sh {command}")
        # os.system(f"{command}")
        pass




    def install_with_cmake(self, name, package, reinstall=False):
        cmake_args = package["cmake_args"] if "cmake_args" in package.keys() else ""
        cmake_args = os.path.expanduser(cmake_args)
        cmake_args = os.path.expandvars(cmake_args)
        if "DCMAKE_INSTALL_PREFIX" not in cmake_args:
            cmake_args = cmake_args + f" -DCMAKE_INSTALL_PREFIX={self.usr_dir}"
        make_args = package["make_args"] if "make_args" in package.keys() else ""
        make_args = os.path.expanduser(make_args)
        make_args = os.path.expandvars(make_args)
        curr_dir = os.curdir
        build_dir = os.path.join(curr_dir, "build")
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)
        os.chdir(build_dir)
        print(f"Command: cmake .. {cmake_args}")
        print(f"Command: cmake --build ./ -- {make_args}")
        print(f"Command:sudo make install")
        # os.system(f"cmake .. {cmd_args}")
        # os.system(f"cmake --build ./ -- {make_args}")
        # os.system(f"sudo make install")
        os.chdir(curr_dir)





        
def main():
    pass
if __name__ == '__main__':
    main()
