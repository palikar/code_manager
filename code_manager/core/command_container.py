import logging
import os

import code_manager.commands
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.importing import import_modules_from_folder
from code_manager.utils.logger import debug_cyan
from code_manager.utils.logger import debug_red


class CommandContainer(ConfigurationAware):

    def __init__(self):
        self.commands = {}
        self.commands_dir = os.path.dirname(code_manager.commands.__file__)

    def load_commands(self):
        import_modules_from_folder(self.commands_dir, 'code_manager.commands', self._add_command)

    def _add_command(self, command, file):
        assert command is not None
        assert file is not None

        if not hasattr(command, 'ExportedClass'):
            debug_red('No exported command class found in file %s', file)
            return

        if command.ExportedClass.name is None:
            debug_red('The exported class does not have proper name.')
            return

        CommandClass = command.ExportedClass  # pylint: disable=C0103

        if CommandClass.name in self.commands.keys():
            debug_red('Command with the name \'%s\' already exists', CommandClass.name)

        debug_cyan('Loading command: \'%s\'', CommandClass.name)

        self.commands[CommandClass.name] = CommandClass

    def execute_command(self, command, args, pack, root):

        if command not in self.commands.keys():
            return

        command_obj = self.commands[command]()

        command_obj.root = root
        command_obj.args = args
        command_obj.pack = pack

        logging.debug('Executing command: \'%s\' on package \'%s\'', command, pack)
        command_obj.execute(args, root)
