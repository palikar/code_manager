import subprocess


class GrepCommand:

    name = 'grep'

    def __init__(self):
        pass

    def execute(self, args, path):

        ret = subprocess.run(['git', '-C', path, 'grep', *args], stdout=subprocess.PIPE)
        return path, ret.returncode, ret.stdout


ExportedClass = GrepCommand
