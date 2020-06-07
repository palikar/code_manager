import logging
import os

from code_manager.core.configuration import ConfigurationAware
from code_manager.core.installation import BasicInstaller
from code_manager.utils.logger import debug_red
from code_manager.utils.utils import sanitize_input_variable


class LdInstaller(BasicInstaller, ConfigurationAware):

    name = 'ld'
    manditory_attr = ['ld']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        paths = self.node['path']
        in_bashrc = self.node.get('in_bashrc', False)

        if isinstance(paths, str):
            paths = [paths]

        paths = map(lambda p: 'export LD_PATH=${{LD_PATH}}:{}'.format(sanitize_input_variable(p)), paths)

        target_file = '~/.bashrc' if in_bashrc else os.path.join(self.code_dir, 'setenv.sh')
        target_file = sanitize_input_variable(target_file)

        with open(target_file) as target:
            target_file_lines = target.read().splitlines()

        with open(target_file, 'a') as target:
            for line in list(paths):
                if line in target_file_lines:
                    debug_red(
                        'Skipping library path export line.\
The line is already in the file: %s', line,
                    )
                    continue

                logging.debug('Adding library export in %s', target_file)
                target.write(line)
                target.write('\n')

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = LdInstaller
