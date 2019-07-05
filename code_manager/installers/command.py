import logging


from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.process import execute_sanitized


class CommandInstaller(BasicInstaller, ConfigurationAware):

    name = 'command'
    manditory_attr = ['command']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        command = []
        command_field = self.node['command']

        if isinstance(command_field, str):
            command.append(command_field)
        elif isinstance(command_field, list):
            command.extend(command_field)

        logging.debug('Running command with: %s', ' '.join(command))
        if execute_sanitized('Command', command, self.root) is None:
            return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = CommandInstaller
