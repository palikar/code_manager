import logging

from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller
from code_manager.utils.process import execute_sanitized


class CommandInstaller(BasicInstaller, ConfigurationAware):

    name = 'command'
    manditory_attr = ['command']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        commands = []
        command_field = self.node['command']

        if isinstance(command_field, str):
            commands.append([command_field])
        elif isinstance(command_field, list):
            if isinstance(command_field[0], str):
                commands.append(command_field)
            else:
                for com in command_field:
                    commands.append(com)

        for command in commands:
            logging.debug('Running command with: %s', command)
            if execute_sanitized('Command', command, self.root) is None:
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = CommandInstaller
