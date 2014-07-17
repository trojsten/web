# -*- coding: utf-8 -*-

import os


def clone(path, url):
    os.system('git clone {} {}'.format(path, url))


def pull(path, url):
    if not os.path.exists(path):
        raise IOError('Path does not exist: %s' % path)
    os.chdir(path)
    os.system('git pull')


def pull_or_clone(path, url):
    try:
        pull(url, path)
    except IOError:
        clone(url, path)
