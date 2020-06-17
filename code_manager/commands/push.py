import logging
import os
import subprocess


class PushCommand:

    name = 'push'

    def execute(self, args, path):
        if not os.path.exists(os.path.join(path, '.git')):
            return 0
        push_command = ['git', 'push', *args.rest]
        logging.debug('Running command: [%s] in %s', ' '.join(push_command), path)
        subprocess.run(push_command, stdout=subprocess.STDOUT, cwd=path)
        return 0


ExportedClass = PushCommand
