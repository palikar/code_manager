import os
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.utils import sanitize_input_variable
from code_manager.utils.process import execute_sanitized


class CopyInstaller(BasicInstaller, ConfigurationAware):

    name = 'cp'
    manditory_attr = ['cp']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        cp_node = self.node['cp']

        for copy in cp_node:
            cp_command = ['cp', '-a', '-v']
            if isinstance(copy['source'], str):
                source = sanitize_input_variable(copy['source'])
                cp_command += [source]
            else:
                source = map(sanitize_input_variable, copy['source'])
                cp_command += source

            dest = sanitize_input_variable(copy['dest'])
            if not os.path.exists(dest):
                os.makedirs(dest)
            cp_command += [dest]

            logging.debug('Running copy command: %s', cp_command)

            if execute_sanitized('cp', cp_command, self.root) is None:
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = CopyInstaller
