import os
import sys
import subprocess

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class CommandInstaller(BasicInstaller, ConfigurationAware):

    name = 'command'

    def __init__(self):
        BasicInstaller.__init__()
        pass

    def execute(self, name):
        pass

    def update(self, name):
        pass


exported_class = CommandInstaller
