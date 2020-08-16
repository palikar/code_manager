import logging
import os
import subprocess
import sys

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import RED
from code_manager.utils.logger import RESET


class PushCommand(ConfigurationAware):

    name = 'push'

    def __init__(self):
        self.color = self.opt.get(
            'Commands', 'push-colors', fallback=True,
        ) == 'true'

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0

        if self.color and not args.no_color:
            color = True
        elif args.no_color:
            color = False

        push_command = ['git', 'push', *args.rest]
        logging.debug(
            'Running command: [%s] in %s',
            ' '.join(push_command), path,
        )
        ret = subprocess.run(
            push_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path,
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

        for line in ret.stderr.splitlines():
            if color:
                sys.stderr.buffer.write(
                    bytes(
                        RED + self.pack + RESET
                        + ':', 'utf-8',
                    ) + line + b'\n',
                )
            else:
                sys.stderr.buffer.write(
                    bytes(self.pack + ':', 'utf-8') + line + b'\n',
                )
        sys.stderr.buffer.flush()

        return 0


ExportedClass = PushCommand
