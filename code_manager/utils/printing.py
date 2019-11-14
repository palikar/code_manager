from subprocess import Popen, PIPE


def less(data):
    process = Popen(["less"], stdin=PIPE)
    try:
        process.stdin.write(data)
        process.communicate()
    except IOError:
        pass
