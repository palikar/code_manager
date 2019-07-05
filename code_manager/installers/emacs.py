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
        # TODO: Check if the right line is already there
        with open(emacs_load_file, 'a') as load_file:
            load_file.write(';; Files from package {}\n'.format(name))
            for el_f in el_files:
                path = os.path.join(self.root, el_f)
                logging.debug('Adding %s to the Emacs load file', path)
                load_file.write('(load-file \"{}\")\n'.format(path))

        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = EmacsInstaller
