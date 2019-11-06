import os
import subprocess
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import debug_red
from code_manager.utils.contextmanagers import output_header


class MakeInstaller(BasicInstaller, ConfigurationAware):

    name = 'make'
    manditory_attr = []

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        make_command = ['make']
        self.append_optional('make_args', make_command)
        build_dir = os.path.join(self.root, 'build/')
        if not os.path.isdir(build_dir):
            build_dir = self.root

        if not os.path.isdir(build_dir):
            debug_red('There is no build directory. Connot run make')
            return None
        logging.debug('Running make with: %s', ' '.join(make_command))
        logging.debug('Build directory: %s', build_dir)

        with output_header("Make"):
            child = subprocess.Popen(make_command,
                                     cwd=build_dir)
            _ = child.communicate()[0]
            ret_code = child.returncode

        if ret_code != 0:
            debug_red('Running make failed')
            return None

        extra_targets = []
        self.get_optional('make_extra_targets', extra_targets.extend)
        for target in extra_targets:
            make_command = ['make']
            self.append_optional('make_args', make_command)
            make_command.append(target)
            logging.debug('Running make with: %s', ' '.join(make_command))

            with output_header("Make"):
                child = subprocess.Popen(make_command,
                                         cwd=build_dir)
                _ = child.communicate()[0]
                ret_code = child.returncode

            if ret_code != 0:
                debug_red('Running make target %s failed', target)
                return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = MakeInstaller
