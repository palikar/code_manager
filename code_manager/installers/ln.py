import logging
import os

from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller
from code_manager.utils.process import execute_sanitized
from code_manager.utils.utils import sanitize_input_variable


class LinkInstaller(BasicInstaller, ConfigurationAware):

    name = 'ln'
    manditory_attr = ['ln']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        ln_node = self.node['ln']

        for copy in ln_node:
            ln_command = ['ln', '-s']
            if isinstance(copy['source'], str):
                source = sanitize_input_variable(copy['source'])
                ln_command += [source]
            else:
                source = map(sanitize_input_variable, copy['source'])
                ln_command += source

            dest = sanitize_input_variable(copy['dest'])
            if not os.path.exists(dest):
                os.makedirs(dest)
            ln_command += [dest]

            logging.debug('Running copy command: %s', ln_command)

            if execute_sanitized('ln', ln_command, self.root) is None:
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = LinkInstaller
