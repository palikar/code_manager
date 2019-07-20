import subprocess


from code_manager.utils.logger import debug_red
from code_manager.utils.contextmanagers import output_header
from code_manager.utils.utils import sanitize_input_variable


def execute_sanitized(name, command, cwd, supress_output=False):
    assert name is not None
    assert command is not None
    assert cwd is not None

    command = list(map(sanitize_input_variable, command))
    stdout = subprocess.PIPE if supress_output else None
    with output_header(name):
        # TODO: This is very dangerous wiht shell=True
        # Think of something better at some point
        child = subprocess.Popen(' '.join(command),
                                 cwd=cwd,
                                 stdout=stdout,
                                 shell=True)
        _ = child.communicate()[0]
        ret_code = child.returncode
    if ret_code != 0:
        debug_red('Running %s failed', name)
        return None
    return 0


def get_output(name, command, cwd, supress_output=False):
    assert name is not None
    assert command is not None
    assert cwd is not None

    command = list(map(sanitize_input_variable, command))

    with output_header(name):
        child = subprocess.Popen(command,
                                 cwd=cwd,
                                 stdout=subprocess.PIPE)
        for line in child.stdout:
            if not supress_output:
                print(line)
                yield line

        _ = child.communicate()[0]
        ret_code = child.returncode
    if ret_code != 0:
        debug_red('Running %s failed', name)
        return None
    return 0
