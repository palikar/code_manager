import logging
import subprocess

from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller
from code_manager.utils.contextmanagers import output_header
from code_manager.utils.logger import debug_red


class NodeJsInstaller(BasicInstaller, ConfigurationAware):

    name = 'nodejs'
    manditory_attr = ['nodejs_scripts']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None
        build_dir = self.root
        extra_scripts = []
        self.get_optional('nodejs_scripts', extra_scripts.extend)
        for target in extra_scripts:
            nodejs_command = ['nodejs']
            self.append_optional('nodejs_args', nodejs_command)
            nodejs_command.append(target)

            logging.debug('Running make with: %s', ' '.join(nodejs_command))

            with output_header('NPM'):
                child = subprocess.Popen(
                    nodejs_command,
                    cwd=build_dir,
                )
                _ = child.communicate()[0]
                ret_code = child.returncode

            if ret_code != 0:
                debug_red('Running npm script %s failed', target)
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = NodeJsInstaller
