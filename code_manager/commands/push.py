import os
import subprocess


class PushCommand:

    name = 'push'

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0
        ret = subprocess.run(['git', 'push', *args], stdout=subprocess.STDOUT, cwd=path)
        return 0


ExportedClass = PushCommand
