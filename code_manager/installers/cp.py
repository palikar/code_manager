import os
import logging

from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.utils import sanitize_input_variable


class CopyInstaller(BasicInstaller, ConfigurationAware):

    name = 'cp'
    manditory_attr = ['cp']

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        cp_node = self.node['cp']
        
        assert isinstance(cp_node, list)

        for copy in cp_node:
            dest = sanitize_input_variable(copy['dest'])
            source = sanitize_input_variable(copy['source'])

            if not os.path.exists():
                os.makedirs(dst)
                
            cp_command = ['cp', '-a', '-v', source, dest]

        


        
        return 0

    def update(self, name):
        return self.execute(name)


ExportedClass = CopyInstaller
