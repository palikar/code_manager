from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller


class PathInstaller(BasicInstaller, ConfigurationAware):

    name = 'path'
    manditory_attr = ['bash_lines']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        pass

    def update(self, name):
        return self.execute(name)


ExportedClass = PathInstaller
