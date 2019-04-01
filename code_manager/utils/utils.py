#!/usr/bin/python

import os
import re


def recursive_items(dictionary, dicts=False):

    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                if dicts:
                    yield (key, value)
                    yield from recursive_items(value, dicts=dicts)
                else:
                    yield from recursive_items(value, dicts=dicts)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, dict) or isinstance(v, list):
                        yield from recursive_items(v, dicts=dicts)
                yield (key, value)
            else:
                yield (key, value)
    elif isinstance(dictionary, list):
        for v in dictionary:
            if isinstance(v, dict) or isinstance(v, list):
                yield from recursive_items(v, dicts=dicts)
        yield (None, dictionary)


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def flatten(xs):
    res = []

    def loop(ys):
        for i in ys:
            if isinstance(i, list):
                loop(i)
            else:
                res.append(i)
    loop(xs)
    return res


def get_emacs_load_file():

    load_file = os.path.expanduser("~/.emacs.d/code-manager-packages.el")
    if not os.path.isfile(load_file):
        with open(load_file, 'w+') as file:
            file.write(";; This file was generated by code-manager\n")
            file.write(";; All the packages of code-manager \
            will be loaded here\n")
            file.write(";; Do not edit this file\n\n")

    emacs_init = os.path.expanduser("~/.emacs")
    if not os.path.isfile(emacs_init):
        emacs_init = "~/.emacs.el"
    if not os.path.isfile(emacs_init):
        emacs_init = "~/.emacs.d/init.el"

    with open(emacs_init, 'r') as file:
        content = file.read()
        match = re.search('(load-file \"~/.emacs.d/code-manager-packages.el\")', content)

    if not match:
        with open(emacs_init, 'a') as file:
            file.write(f'\n\n;; This \'load-file\' is added by code-manager \n')
            file.write(f';; It loads the packages installed by code-manager\n')
            file.write(f';; Do not delete the line nor the file\n')
            file.write(f'(load-file \"~/.emacs.d/code-manager-packages.el\")')

    return load_file
