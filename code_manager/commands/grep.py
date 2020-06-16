import subprocess
import sys

import code_manager.utils.logger

class GrepCommand:

    name = 'grep'

    def execute(self, args, path):

        ret = subprocess.run(['grep', '-r', *args], stdout=subprocess.PIPE, cwd=path)

        for line in ret.stdout.splitlines():
            sys.stdout.buffer.write(bytes(self.pack + ':', 'utf-8') + line + b'\n')
            sys.stdout.buffer.flush()

        return 0 


ExportedClass = GrepCommand
