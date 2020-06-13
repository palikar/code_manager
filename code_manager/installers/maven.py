import logging
import os
import subprocess

from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller
from code_manager.utils.contextmanagers import output_header
from code_manager.utils.logger import debug_red


class MavenInstaller(BasicInstaller, ConfigurationAware):

    name = 'maven'
    manditory_attr = ['maven_targets']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        extra_targets = []
        self.get_optional('maven_targets', extra_targets.extend)
        for target in extra_targets:
            maven_command = ['mvn']
            self.append_optional('maven_args', maven_command)
            maven_command.append(target)

            logging.debug('Running maven with: %s', ' '.join(maven_command))

            with output_header('Maven'):
                child = subprocess.Popen(
                    maven_command,
                    cwd=build_dir,
                )
                _ = child.communicate()[0]
                ret_code = child.returncode

            if ret_code != 0:
                debug_red('Running maven target %s failed', target)
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = MavenInstaller
