import sys

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import RED
from code_manager.utils.logger import RESET


class RootCommand(ConfigurationAware):

    name = 'root'

    def __init__(self):
        self.color = False if self.opt.get('Commands', 'root-colors', fallback=True) == 'false' else True

    def execute(self, args, path):

        if self.color and not args.no_color:
            color = True
        elif args.no_color:
            color = False

        line = bytes(path, 'utf-8')
        if color:
            sys.stdout.buffer.write(bytes(RED + self.pack + RESET + ':', 'utf-8') + line + b'\n')
        else:
            sys.stdout.buffer.write(bytes(self.pack + ':', 'utf-8') + line + b'\n')

        sys.stdout.buffer.flush()

        return 0


ExportedClass = RootCommand
