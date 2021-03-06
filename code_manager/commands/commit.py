import logging
import os
import subprocess
import sys

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import RED
from code_manager.utils.logger import RESET


class CommitCommand(ConfigurationAware):

    name = 'commit'

    def __init__(self):
        self.color = self.opt.get(
            'Commands', 'commit-colors', fallback=True,
        ) == 'true'

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0

        color = self.color and not args.no_color

        msg = args.message
        msg += '\n\n\nCreated by code-manager'
        msg = f'"{msg}"'

        push_command = ['git', 'commit', '-m', msg]
        push_command.extend(args.rest)

        logging.debug(
            'Running command: [%s] in %s',
            ' '.join(push_command), path,
        )
        ret = subprocess.run(push_command, stdout=subprocess.PIPE, cwd=path)

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


ExportedClass = CommitCommand
