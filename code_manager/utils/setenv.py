from os import path


def get_default_setenv(args, opt):
    content = []

    content += ["export CODE_DIR={}".format(opt['Config']['code'])]
    content += ["export USR_DIR={}".format(opt['Config']['usr'])]
    content += ["export LD_PATH=LD_PATH:{}".format(opt['Config']['usr'])]
    content += ["source {}".format(path.join(opt['Config']['venv'], 'bin', 'activate'))]

    return "".join(list(map(lambda x: x + '\n', content)))
