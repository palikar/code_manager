import logging
import os
import subprocess
import sys

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import CYAN
from code_manager.utils.logger import RED
from code_manager.utils.logger import RESET


class SedCommand(ConfigurationAware):

    name = 'sed'

    def __init__(self):
        self.color = self.opt.get(
            'Commands', 'sed-colors', fallback=True,
        ) == 'true'

    def execute(self, args, path):

        if self.color and not args.no_color:
            color = True
        elif args.no_color:
            color = False

        if not os.path.exists(os.path.join(path, '.git')):
            find_command = ['find', '-name', args.files]
            logging.debug(
                'Running command: [%s] in %s', ' '.join(find_command), path,
            )
            ret = subprocess.run(
                find_command, stdout=subprocess.PIPE, cwd=path, check=False,
            )
        else:
            git_command = ['git', 'ls-files', args.files]
            logging.debug(
                'Running command: [%s] in %s', ' '.join(git_command), path,
            )
            ret = subprocess.run(
                git_command, stdout=subprocess.PIPE, cwd=path, check=False,
            )

        files = ret.stdout.splitlines()

        for file_name in files:
            file_name = file_name.decode('utf-8')
            sed_command = ['sed']
            if args.inplace:
                sed_command.append('-i')
            sed_command.extend(args.sed_args)
            sed_command.extend(['-e', args.expression, file_name])

            logging.debug(
                'Running command: [%s] in ', ' '.join(sed_command), path,
            )
            ret = subprocess.run(
                sed_command, stdout=subprocess.PIPE, cwd=path, check=False,
            )

            for line in ret.stdout.splitlines():
                if color:
                    sys.stdout.buffer.write(
                        bytes(
                            RED + self.pack + RESET + ':' + CYAN + file_name + RESET + ':', 'utf-8',
                        ) + line + b'\n',
                    )
                else:
                    sys.stdout.buffer.write(
                        bytes(
                            self.pack + ':' + file_name
                            + ':', 'utf-8',
                        ) + line + b'\n',
                    )
            sys.stdout.buffer.flush()

        return 0


ExportedClass = SedCommand
