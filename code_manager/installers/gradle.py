import logging
import os
import subprocess

from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller
from code_manager.utils.contextmanagers import output_header
from code_manager.utils.logger import debug_red


class GradleInstaller(BasicInstaller, ConfigurationAware):

    name = 'gradle'
    manditory_attr = ['gradle_targets']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        extra_targets = []
        self.get_optional('gradle_targets', extra_targets.extend)
        for target in extra_targets:
            gradle_command = ['gradle']
            self.append_optional('gradle_args', gradle_command)
            gradle_command.append(target)

            logging.debug('Running gradle with: %s', ' '.join(gradle_command))

            with output_header('Gradle'):
                child = subprocess.Popen(
                    gradle_command,
                    cwd=build_dir,
                )
                _ = child.communicate()[0]
                ret_code = child.returncode

            if ret_code != 0:
                debug_red('Running gradle target %s failed', target)
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = GradleInstaller
