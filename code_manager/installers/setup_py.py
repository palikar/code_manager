from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class SetupPyInstaller(BasicInstaller, ConfigurationAware):

    name = 'setuppy'

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        return 0

    def update(self, name):
        return 0


ExportedClass = SetupPyInstaller
