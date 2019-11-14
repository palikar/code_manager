import os
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.utils import get_emacs_load_file


class EmacsInstaller(BasicInstaller, ConfigurationAware):

    name = 'emacs'
    manditory_attr = ['el_files']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        el_files = self.node['el_files']
        emacs_load_file = get_emacs_load_file()
        logging.debug('Emacs file: %s', emacs_load_file)

        with open(emacs_load_file, 'r') as load_file:
            emacs_load_file_lines = load_file.readlines()

        with open(emacs_load_file, 'a') as load_file:
            for el_f in el_files:
                path = os.path.join(self.root, el_f)
                line = '(load-file \"{}\")\n'.format(path)

                if line not in emacs_load_file_lines:
                    logging.debug('Adding %s to the Emacs load file', path)
                    load_file.write(';; Files from package {}\n'.format(name))
                    load_file.write(line)

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = EmacsInstaller
