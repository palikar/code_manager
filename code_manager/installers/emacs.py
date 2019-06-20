from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class EmacsInstaller(BasicInstaller, ConfigurationAware):

    name = 'emacs'

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        return 0

    def update(self, name):
        return 0


ExportedClass = EmacsInstaller
