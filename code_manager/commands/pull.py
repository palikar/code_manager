import os
import subprocess


class PullCommand:

    name = 'pull'

    def __init__(self):
        pass

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0
        ret = subprocess.run(['git', 'pull', *args], stdout=subprocess.STDOUT, cwd=path)
        return 0


ExportedClass = PullCommand
