from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class CommandInstaller(BasicInstaller, ConfigurationAware):

    name = 'command'

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        return 0

    def update(self, name):
        return 0


ExportedClass = CommandInstaller
