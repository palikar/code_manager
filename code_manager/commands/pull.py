import logging
import os
import subprocess


class PullCommand:

    name = 'pull'

    def __init__(self):
        pass

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0
        push_command = ['git', 'pull', *args.rest]
        logging.debug('Running command: [%s] in %s', ' '.join(push_command), path)
        subprocess.run(push_command, stdout=subprocess.STDOUT, cwd=path)
        return 0


ExportedClass = PullCommand
