import logging
import subprocess
import sys

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import RED
from code_manager.utils.logger import RESET


class GrepCommand(ConfigurationAware):

    name = 'grep'

    def __init__(self):
        self.color = self.opt.get(
            'Commands', 'grep-colors', fallback=True,
        ) == 'true'

    def execute(self, args, path):
        grep_command = ['grep', '-r']

        if self.color and not args.no_color:
            color = True
            grep_command.append('--color=always')
        else:
            color = False
            grep_command.append('--color=never')

        grep_command.extend(args.rest)

        logging.debug(
            'Running command: [%s] in %s',
            ' '.join(grep_command), path,
        )
        ret = subprocess.run(
            grep_command, stdout=subprocess.PIPE, cwd=path, check=False,
        )

        for line in ret.stdout.splitlines():
            if color:
                sys.stdout.buffer.write(
                    bytes(
                        RED + self.pack + RESET
                        + ':', 'utf-8',
                    ) + line + b'\n',
                )
            else:
                sys.stdout.buffer.write(
                    bytes(self.pack + ':', 'utf-8') + line + b'\n',
                )
        sys.stdout.buffer.flush()

        return 0


ExportedClass = GrepCommand
