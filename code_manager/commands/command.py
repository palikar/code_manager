import logging
import os
import subprocess
import sys

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import RED
from code_manager.utils.logger import RESET


class CommandCommand(ConfigurationAware):

    name = 'command'

    def __init__(self):
        self.color = self.opt.get(
            'Commands', 'command-colors', fallback=True,
        ) == 'true'

    def execute(self, args, path):

        if args.git and not os.path.exists(os.path.join(path, '.git')):
            return 0

        color = self.color and not args.no_color

        command = args.rest
        logging.debug('Running command: [%s] in %s', ' '.join(command), path)
        ret = subprocess.run(
            command, stdout=subprocess.PIPE, cwd=path, check=False,
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


ExportedClass = CommandCommand
