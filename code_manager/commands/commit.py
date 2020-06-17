import logging
import os
import subprocess


class CommitCommand:

    name = 'commit'

    def __init__(self):
        pass

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0

        msg = args.message
        msg += '\n\n\nCreated by code-manager'
        msg = f'"{msg}"'

        push_command = ['git', 'commit', '-m', msg]
        push_command.extend(args.rest)

        logging.debug('Running command: [%s] in %s', ' '.join(push_command), path)
        subprocess.run(push_command, stdout=subprocess.STDOUT, cwd=path)

        return 0


ExportedClass = CommitCommand
