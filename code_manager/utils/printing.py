from subprocess import PIPE
from subprocess import Popen

from code_manager.utils.logger import RESET


def less(data):
    process = Popen(['less'], stdin=PIPE)
    try:
        process.stdin.write(data)
        process.communicate()
    except OSError:
        pass

def colorize(string, color, enable=True):
    if enable:
        return color + string + RESET
    else:
        return string
    
