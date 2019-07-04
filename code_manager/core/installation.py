import os
import logging
from abc import abstractmethod

from code_manager.utils.logger import debug_red
from code_manager.utils.logger import debug_cyan
from code_manager.utils.utils import sanitize_input_variable
from code_manager.utils.importing import import_modules_from_folder
from code_manager.core.configuration import ConfigurationAware

import code_manager.installers


class BasicInstaller(ConfigurationAware):

    name = None
    manditory_attr = []
    node = {}

    def __init__(self):
        pass

    def get_optional(self, attr, action=None):
        assert attr is not None

        if attr in self.node.keys():
            value = self.node[attr]
            if action is not None and value.strip() != '':
                if not hasattr(action, '__call__'):
                    raise AttributeError('Action must be callable')
                action(value)

    def append_optional(self, attr, command):
        assert attr is not None
        assert isinstance(command, list)

        self.get_optional(attr,
                          lambda arg: command.append(sanitize_input_variable(arg)))
        return command

    def append_manditory(self, attr, command):
        assert attr is not None
        assert isinstance(command, list)

        command.apend(sanitize_input_variable(self.node[attr]))

        return command

    @abstractmethod
    def execute(self, name):
        raise NotImplementedError('All installers need to implement the execute method.')

    @abstractmethod
    def update(self, name):
        raise NotImplementedError('All installers need to implement the update method.')


class Installation(ConfigurationAware):

    installers = {}
    installer_objects = {}
    update = False
    root = None

    def __init__(self):
        self.installers_dir = os.path.dirname(code_manager.installers.__file__)

    def load_installer(self):
        logging.debug('Initializing the installation system')
        logging.debug('Install scripts directroy: %s', self.installers_dir)

        import_modules_from_folder(self.installers_dir, 'code_manager.installers', self._add_installer)

    def _add_installer(self, installer, file):
        assert installer is not None
        assert file is not None

        if not hasattr(installer, 'ExportedClass'):
            debug_red('No exported class found in file %s', file)
            return

        if issubclass(installer.ExportedClass, BasicInstaller) is None:
            debug_red('The exported class is not a subclass of BasicInstaller.')
            return

        if installer.ExportedClass.name is None:
            debug_red('The exported class does not have proper name.')
            return

        InstallerClass = installer.ExportedClass  # pylint: disable=C0103
        if InstallerClass.name in self.installers.keys():
            debug_red('Installer with the name \'%s\' already exists', InstallerClass.name)

        debug_cyan('Loading installer: \'%s\'', InstallerClass.name)
        self.installers[InstallerClass.name] = InstallerClass

    def run_installer(self, name, installer):

        if installer not in self.installers.keys():
            logging.critical('There is no installer with the name %s', installer)

        if installer not in self.installer_objects.keys():
            installer_obj = self.installers[installer]()
            self.installer_objects[installer] = installer_obj
        else:
            installer_obj = self.installer_objects[installer]

        node = self.packages[name]
        installer_obj.node = node
        installer_obj.root = self.root

        if hasattr(installer_obj, 'manditory_attr') and isinstance(installer_obj.manditory_attr, list):
            for attr in installer_obj.manditory_attr:
                if attr not in node.keys():
                    logging.critical('The attribute %s is mandatory for the installer %s\
but it is not in the package node of %s.',
                                     attr, installer_obj.name, name)
        if self.update:
            result = installer_obj.update(name)
        else:
            result = installer_obj.execute(name)

        if result is None:
            logging.critical('The installer [%s] failed to execute properly', installer_obj.name)

    def install(self, package, root, update=False):
        assert package is not None
        node = self.packages[package]

        if 'install' not in node.keys():
            return 0

        self.update = update
        self.root = root

        installer = node['install']
        if isinstance(installer, str):
            self.run_installer(package, installer)
            return 0
        elif isinstance(installer, list):
            for inst in installer:
                self.run_installer(package, inst)
            return 0
        else:
            logging.critical('Can\'t install %s.\
Installation node is nor a list, nor a string.', package)
            exit(1)
            return None


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
