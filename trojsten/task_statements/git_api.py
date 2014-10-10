# -*- coding: utf-8 -*-
import os
import subprocess


def clone(path, url):
    return subprocess.call(['git', 'clone', path, url])


def pull(path, url):
    if not os.path.exists(path):
        raise IOError('Path does not exist: %s' % path)
    return subprocess.call(['git', 'pull', '--git-dir=%s' % path])


def pull_or_clone(path, url):
    try:
        pull(url, path)
    except IOError:
        clone(url, path)
