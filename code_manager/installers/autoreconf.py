import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.process import execute_sanitized


class AutoreconfInstaller(BasicInstaller, ConfigurationAware):

    name = 'autoreconf'
    manditory_attr = []

    def __init__(self):
        BasicInstaller.__init__(self)

    def _do_execute(self, name):
        assert name is not None

        autoreconf_command = ['sh', 'autoreconf']
        build_dir = self.root

        self.append_optional('autoreconf_args', autoreconf_command)

        logging.debug('Running autoreconf with: %s', ' '.join(autoreconf_command))
        logging.debug('Build directory: %s', build_dir)

        if execute_sanitized('Autoreconf', autoreconf_command, self.root) is None:
            return None

        return 0

    def execute(self, name):
        return self._do_execute(name)

    def update(self, name):
        return self._do_execute(name)


ExportedClass = AutoreconfInstaller
