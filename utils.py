#!/usr/bin/python

import os, sys
import collections


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


def main():
    pass
if __name__ == '__main__':
    main()
