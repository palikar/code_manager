import os
import subprocess
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import debug_red


class CmakeInstaller(BasicInstaller, ConfigurationAware):

    name = 'cmake'

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        cmake_command = ['cmake']

        cmake_command.append('-S')
        cmake_command.append(self.root)

        self.append_optional('cmake_args', cmake_command)

        if 'DCMAKE_INSTALL_PREFIX' not in cmake_command[-1]:
            cmake_command.append('-DCMAKE_INSTALL_PREFIX={}'.format(self.usr_dir))

        build_dir = os.path.join(self.root, 'build/')

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        logging.debug('Running cmake with: %s', ' '.join(cmake_command))
        logging.debug('Build directory: %s', build_dir)

        # TODO: Abstract this into a context control
        print("Cmake output =================>\n")
        child = subprocess.Popen(cmake_command,
                                 cwd=build_dir)

        _ = child.communicate()[0]
        ret_code = child.returncode
        print("\n<================= Cmake output ")

        if ret_code != 0:
            debug_red('Running cmake failed')
            return None

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = CmakeInstaller
