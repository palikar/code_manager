import os
import subprocess
import logging
import tempfile

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.utils import sanitize_input_variable
from code_manager.utils.logger import debug_red


class BashrcInstaller(BasicInstaller, ConfigurationAware):

    name = 'bashrc'
    manditory_attr = ['bash_lines']

    def __init__(self):
        BasicInstaller.__init__(self)

    @staticmethod
    def _check_line(line):
        temp_fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(temp_fd, 'w') as tmp:
                tmp.write(line)
            with open(os.devnull, 'w') as null:
                proc = subprocess.Popen(['bash', path], stdout=null, stderr=null)
                _ = proc.communicate()[0]
                return_code = proc.returncode
        finally:
            os.remove(path)
        return return_code == 0

    def execute(self, name):
        assert name is not None

        bash_lines = self.node['bash_lines']
        in_bashrc = self.node.get('in_bashrc', False)

        if isinstance(bash_lines, str):
            bash_lines = [sanitize_input_variable(bash_lines)]
        else:
            bash_lines = map(sanitize_input_variable, bash_lines)

        target_file = '~/.bashrc' if in_bashrc else os.path.join(self.code_dir, 'setenv.sh')
        target_file = sanitize_input_variable(target_file)

        with open(target_file, 'r') as target:
            target_file_lines = target.readlines()

        with open(target_file, 'a') as target:
            for line in bash_lines:

                if not BashrcInstaller._check_line(line):
                    debug_red('Skipping bash line.\
 The line is invalid:%s', line)
                    continue

                if line in target_file_lines:
                    debug_red('Skipping bash line.\
 The line is already in the file:%s', line)
                    continue
                logging.debug('Writing bahs line in %s', target_file)
                target.write(line)

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = BashrcInstaller
