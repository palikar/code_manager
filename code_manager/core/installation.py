import logging
import os
import sys
from abc import abstractmethod

import code_manager.installers
from code_manager.core.configuration import CofigurationResolver
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.importing import import_modules_from_folder
from code_manager.utils.logger import debug_cyan
from code_manager.utils.logger import debug_red
from code_manager.utils.logger import info_blue
from code_manager.utils.utils import sanitize_input_variable


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
            if not hasattr(action, '__call__'):
                raise AttributeError('Action must be callable')

            if isinstance(value, str) and value.strip() != '':
                action(value)

            if isinstance(value, list) and value:
                action(value)

    def append_optional(self, attr, command):
        assert attr is not None
        assert isinstance(command, list)

        self.get_optional(
            attr,
            lambda arg: command.append(sanitize_input_variable(arg)),
        )
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
        self.resolver = CofigurationResolver()

        self.resolver.variables['code_dir'] = self.code_dir
        self.resolver.variables['usr_dir'] = self.usr_dir

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

    def _expand_package_node(self, node):
        return self.resolver.resolve_nodes(node)

    def run_installer(self, name, installer, node):
        assert name is not None
        assert installer is not None

        if installer not in self.installers.keys():
            logging.critical('There is no installer with the name %s', installer)

        if installer not in self.installer_objects.keys():
            installer_obj = self.installers[installer]()
            self.installer_objects[installer] = installer_obj
        else:
            installer_obj = self.installer_objects[installer]

        installer_obj.node = node
        installer_obj.root = self.root

        if hasattr(installer_obj, 'manditory_attr') and isinstance(installer_obj.manditory_attr, list):
            for attr in installer_obj.manditory_attr:
                if attr not in node.keys():
                    logging.critical(
                        'The attribute %s is mandatory for the installer %s\
but it is not in the package node of %s.', attr, installer_obj.name, name,
                    )

        info_blue('Running installer: %s', installer_obj.name)
        if self.update:
            result = installer_obj.update(name)
        else:
            result = installer_obj.execute(name)

        if result is None:
            logging.critical('The installer [%s] failed to execute properly', installer_obj.name)

    def install(self, package, root, node, update=False):
        assert package is not None
        assert node is not None
        assert root is not str

        if 'install' not in node.keys():
            return 0

        self.update = update
        self.root = root

        self.resolver.variables['root'] = self.root

        node = self._expand_package_node(node)

        installer = node['install']
        if isinstance(installer, str):
            self.run_installer(package, installer, node)
            return 0
        elif isinstance(installer, list):
            for inst in installer:
                self.run_installer(package, inst, node)
            return 0
        else:
            logging.critical(
                'Can\'t install %s.\
Installation node is nor a list, nor a string.', package,
            )
            sys.exit(1)
            return None
