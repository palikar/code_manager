import os
import shutil


def move_tree(src, dst, symlinks=False, ignore=None):
    assert src is not None
    assert dst is not None

    for item in os.listdir(src):
        source = os.path.join(src, item)
        dest = os.path.join(dst, item)
        if os.path.isdir(source):
            shutil.move(source, dest)
        else:
            shutil.move(source, dest)
