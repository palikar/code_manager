import os
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.process import execute_sanitized


class AutoreconfInstaller(BasicInstaller, ConfigurationAware):

    name = 'pip'
    manditory_attr = []

    def __init__(self):
        BasicInstaller.__init__(self)

    def _do_execute(self, name):
        assert name is not None

        pip_command = ['pip', 'install']
        build_dir = self.root

        self.append_optional('pip_args', pip_command)

        if os.path.isfile(os.path.join(build_dir, 'requirements.txt')):
            pip_command.append('-r')
            pip_command.append('requirements.txt')

        self.append_optional('pip_packages', pip_command)

        logging.debug('Running autoreconf with: %s', ' '.join(pip_command))
        logging.debug('Build directory: %s', build_dir)

        if execute_sanitized('pip', pip_command, self.root) is None:
            return None

        return 0

    def execute(self, name):
        return self._do_execute(name)

    def update(self, name):
        return self._do_execute(name)


ExportedClass = AutoreconfInstaller
