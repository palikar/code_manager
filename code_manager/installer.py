import os


class Installer:

    def __init__(self, usr_dir, install_scripts_dir, noinstall=True):
        self.installers = dict()
        self.installers['script'] = self.install_with_script
        self.installers['command'] = self.install_with_command
        self.installers['cmake'] = self.install_with_cmake
        self.installers['setup.py'] = self.install_with_setup_py
        self.usr_dir = usr_dir
        self.noinstall = noinstall
        self.install_scripts_dir = install_scripts_dir

    def install(self, name, package, reinstall=False):
        if self.noinstall:
            return 0
        if package['install'] not in self.installers.keys():
            print('Unknown installer {} \
            for package {name}'.format(package['install']))
            return -1
        else:
            return self.installers[package['install']](name,
                                                       package,
                                                       reinstall=reinstall)

    def install_with_script(self, name, package, reinstall=False):
        print(f'Installing {name} with script file')

        assert(name is not None)
        assert(package is not None)
        assert('script' in package)

        script = os.path.join(self.install_scripts_dir, package['script'])
        script = os.path.expanduser(script)
        script = os.path.expandvars(script)
        script = os.path.abspath(script)
        print(f'Used script: {script}')
        cmd_args = package['script_args'] if 'script_args' in package else ''
        cmd_args = os.path.expanduser(cmd_args)
        cmd_args = os.path.expandvars(cmd_args)
        cmd_args = cmd_args + (' -r' if reinstall else '')
        cmd_args = cmd_args + f'-p {self.usr_dir}'
        print(f'Command: sh {script} {cmd_args}')
        return os.system(f'sh {script} ' + cmd_args)

    def install_with_command(self, name, package, reinstall=False):
        print(f'Installing {name} with command')

        assert(name is not None)
        assert(package is not None)
        assert('command' in package)

        command = (
            package['command'] if reinstall is False
            else package['reinstall_command'])
        command = os.path.expanduser(command)
        command = os.path.expandvars(command)
        print(f'Command: sh {command}')
        return os.system(f'{command}')

    def install_with_setup_py(self, name, package, reinstall=False):

        assert(name is not None)
        assert(package is not None)

        if not os.path.isfile('setup.py'):
            print('There isn\'t a setup.py file at the root of the package.')
            return -1

        setup_args = (package['setup_args']
                      if 'setup_args' in package.keys() else '')
        setup_args = os.path.expanduser(setup_args)
        setup_args = os.path.expandvars(setup_args)

        prefix = self.usr_dir
        command = f'python setup.py install --prefix {prefix} {setup_args}'
        print(f'Command: sh {command}')
        return os.system(f'{command}')

    def install_with_cmake(self, name, package, reinstall=False):
        assert(name is not None)
        assert(package is not None)

        cmake_args = (package['cmake_args']
                      if 'cmake_args' in package.keys() else '')
        cmake_args = os.path.expanduser(cmake_args)
        cmake_args = os.path.expandvars(cmake_args)
        if 'DCMAKE_INSTALL_PREFIX' not in cmake_args:
            cmake_args = cmake_args + f' -DCMAKE_INSTALL_PREFIX={self.usr_dir}'
        make_args = (package['make_args']
                     if 'make_args' in package.keys() else '')
        make_args = os.path.expanduser(make_args)
        make_args = os.path.expandvars(make_args)
        curr_dir = os.curdir
        build_dir = os.path.join(curr_dir, 'build')
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)
        os.chdir(build_dir)
        print(f'Command: cmake .. {cmake_args}')
        print(f'Command: cmake --build ./ -- {make_args}')
        print(f'Command:sudo make install')
        res = os.system('cmake .. {} && cmake --build ./ \
            -- {} && sudo make install'.format(cmake_args, make_args))
        return res
