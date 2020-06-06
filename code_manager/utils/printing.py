from subprocess import PIPE
from subprocess import Popen


def less(data):
    process = Popen(['less'], stdin=PIPE)
    try:
        process.stdin.write(data)
        process.communicate()
    except OSError:
        pass
