from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class EmacsInstaller(BasicInstaller, ConfigurationAware):

    name = 'emacs'

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        pass

    def update(self, name):
        pass


ExportedClass = EmacsInstaller
