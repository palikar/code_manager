import subprocess
import sys

import code_manager.utils.logger

class SedCommand:

    name = 'sed'

    def execute(self, args, path):
        ret = subprocess.run(['sed', *args], stdout=subprocess.PIPE, cwd=path)    
        return 0 


ExportedClass = SedCommand
