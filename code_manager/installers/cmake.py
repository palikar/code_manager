from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class CmakeInstaller(BasicInstaller, ConfigurationAware):

    name = 'cmake'

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        pass

    def update(self, name):
        pass


ExportedClass = CmakeInstaller
