import os
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.process import execute_sanitized


class ScriptInstaller(BasicInstaller, ConfigurationAware):

    name = 'scripts'
    manditory_attr = ['script']

    def __init__(self):
        BasicInstaller.__init__(self)
        self.reinstall = False

    def execute(self, name):
        assert name is not None

        script_command = ['sh']

        script_file = os.path.join(self.install_scripts_dir, self.node['script'])
        script_file = os.path.abspath(script_file)

        if not os.path.isfile(script_file):
            pass

        script_command.append(script_file)
        self.append_optional('script_args', script_command)

        script_command.append('-p')
        script_command.append(self.usr_dir)

        if self.reinstall:
            script_command.append('-r')

        logging.debug('Running script with: %s', ' '.join(script_command))
        if execute_sanitized('Script', script_command, self.root) is None:
            return None

        return 0

    def update(self, name):
        self.reinstall = True
        return self.execute(name)


ExportedClass = ScriptInstaller
