import os
import logging
from abc import abstractmethod

from code_manager.utils.logger import debug_red
from code_manager.utils.logger import debug_cyan
from code_manager.utils.importing import import_modules_from_folder
from code_manager.core.configuration import ConfigurationAware

import code_manager.installers


class BasicInstaller(ConfigurationAware):

    name = None
    manditory_attr = []
    node = {}

    def __init__(self):
        pass

    def get_optional(self, attr, action):

        if not hasattr(action, '__call__'):
            raise AttributeError('Action must be callable')

        if attr in self.node.keys():
            action(self.node[attr])

    @abstractmethod
    def execute(self, name):
        raise NotImplementedError('All installers need to implement the execute method.')

    @abstractmethod
    def update(self, name):
        raise NotImplementedError('All installers need to implement the execute method.')


class Installation(ConfigurationAware):

    installers = {}
    installer_objects = {}

    def __init__(self):
        self.installers_dir = os.path.dirname(code_manager.installers.__file__)

    def load_installer(self):
        logging.debug('Initializing the installation system')
        logging.debug('Install scripts directroy: %s', self.installers_dir)

        import_modules_from_folder(self.installers_dir, 'code_manager.installers', self._add_installer)

    def _add_installer(self, installer, file):
        assert installer is not None
        assert file is not None

        if not hasattr(installer, 'exported_class'):
            debug_red('No exported class found in file %s', file)
            return

        if issubclass(installer.exported_class, BasicInstaller) is None:
            debug_red('The exported class is not a subclass of BasicInstaller.')
            return

        if installer.exported_class.name is None:
            debug_red('The exported class does not have proper name.')
            return

        InstallerClass = installer.exported_class  # pylint: disable=C0103
        debug_cyan('Loading installer: \'%s\'', InstallerClass.name)
        self.installers[InstallerClass.name] = InstallerClass

    def run_installer(self, name, installer):

        if installer not in self.installers.keys():
            logging.critical('There is no installer with the name %s', name)

        if installer not in self.installer_objects.keys():
            installer_obj = self.installers[installer]()
            self.installer_objects[installer] = installer_obj
        else:
            installer_obj = self.installer_objects[installer]

        node = self.packages()[name]
        installer_obj.node = node

        if hasattr(installer_obj, 'manditory_attr') and isinstance(installer_obj.manditory_attr, list):
            for attr in installer_obj.manditory_attr:
                if attr not in node.keys():
                    logging.critical('The attribute %s is mandatory for the installer %s\
                    but it is not in the package node.',
                                     attr, installer_obj.name)

        result = installer_obj.execute(name)

        if result > 0:
            logging.critical('The installer %s failed to execute properly', installer_obj.nam)


# class Installer:

#     def __init__(self,
#                  usr_dir, install_scripts_dir,
#                  noinstall=True):

#         self.installers = dict()
#         self.installers['script'] = self.install_with_script
#         self.installers['command'] = self.install_with_command
#         self.installers['cmake'] = self.install_with_cmake
#         self.installers['setup.py'] = self.install_with_setup_py
#         self.installers['emacs'] = self.install_with_emacs

#         self.usr_dir = usr_dir
#         self.noinstall = noinstall
#         self.install_scripts_dir = install_scripts_dir

#         self._load_extra_installers()

#     def _load_extra_installers(self):
#         pass

#     def install(self, name, package, reinstall=False):
#         if self.noinstall:
#             return 0
#         if package['install'] not in self.installers.keys():
#             print('Unknown installer {} \
#             for package {name}'.format(package['install']))
#             return -1
#         else:
#             return self.installers[package['install']](name,
#                                                        package,
#                                                        reinstall=reinstall)

#     def install_with_script(self, name, package, reinstall=False):
#         print(f'Installing {name} with script file')

#         assert(name is not None)
#         assert(package is not None)
#         assert('script' in package)

#         script = os.path.join(self.install_scripts_dir, package['script'])
#         script = os.path.expanduser(script)
#         script = os.path.expandvars(script)
#         script = os.path.abspath(script)
#         print(f'Used script: {script}')
#         cmd_args = package['script_args'] if 'script_args' in package else ''
#         cmd_args = os.path.expanduser(cmd_args)
#         cmd_args = os.path.expandvars(cmd_args)
#         cmd_args = cmd_args + (' -r' if reinstall else '')
#         cmd_args = cmd_args + f'-p {self.usr_dir}'
#         print(f'Command: sh {script} {cmd_args}')
#         return os.system(f'sh {script} ' + cmd_args)

#     def install_with_command(self, name, package, reinstall=False):
#         print(f'Installing {name} with command')

#         assert(name is not None)
#         assert(package is not None)
#         assert('command' in package)

#         command = (
#             package['command'] if reinstall is False
#             else package['reinstall_command'])
#         command = os.path.expanduser(command)
#         command = os.path.expandvars(command)
#         print(f'Command: sh {command}')
#         return os.system(f'{command}')

#     def install_with_setup_py(self, name, package, reinstall=False):

#         assert(name is not None)
#         assert(package is not None)

#         if not os.path.isfile('setup.py'):
#             print('There isn\'t a setup.py file at the root of the package.')
#             return -1

#         setup_args = (package['setup_args']
#                       if 'setup_args' in package.keys() else '')
#         setup_args = os.path.expanduser(setup_args)
#         setup_args = os.path.expandvars(setup_args)

#         prefix = self.usr_dir
#         command = f'python setup.py install --prefix {prefix} {setup_args}'
#         print(f'Command: sh {command}')
#         return os.system(f'{command}')

#     def install_with_cmake(self, name, package, reinstall=False):
#         assert(name is not None)
#         assert(package is not None)

#         cmake_args = (package['cmake_args']
#                       if 'cmake_args' in package.keys() else '')
#         cmake_args = os.path.expanduser(cmake_args)
#         cmake_args = os.path.expandvars(cmake_args)
#         if 'DCMAKE_INSTALL_PREFIX' not in cmake_args:
#             cmake_args = cmake_args + f' -DCMAKE_INSTALL_PREFIX={self.usr_dir}'
#         make_args = (package['make_args']
#                      if 'make_args' in package.keys() else '')
#         make_args = os.path.expanduser(make_args)
#         make_args = os.path.expandvars(make_args)
#         curr_dir = os.curdir
#         build_dir = os.path.join(curr_dir, 'build')
#         if not os.path.isdir(build_dir):
#             os.makedirs(build_dir)
#         os.chdir(build_dir)
#         print(f'Command: cmake .. {cmake_args}')
#         print(f'Command: cmake --build ./ -- {make_args}')
#         print(f'Command:sudo make install')
#         res = os.system('cmake .. {} && cmake --build ./ \
#             -- {} && sudo make install'.format(cmake_args, make_args))
#         return res

#     def install_with_emacs(self, name, package, reinstall=False):
#         assert(name is not None)
#         assert(package is not None)

#         if 'el_files' not in package.keys():
#             return 0

#         emacs_load_file = get_emacs_load_file()

#         load_file = open(emacs_load_file, 'a')
#         load_file.write(f';; Files from package {name}\n')
#         el_files = package['el_files']
#         for el_f in el_files:
#             path = os.path.join(os.getcwd(), el_f)
#             load_file.write(f'(load-file \"{path}\")\n')
#         load_file.close()

#         return 0
