# -*- coding: utf-8 -*-

import os
import subprocess


def clone(path, url):
    p = subprocess.Popen(['git', 'clone', path, url])
    p.wait()
    return p.returncode


def pull(path, url):
    if not os.path.exists(path):
        raise IOError('Path does not exist: %s' % path)
    os.chdir(path)
    p = subprocess.Popen(['git', 'pull'])
    p.wait()
    return p.returncode


def pull_or_clone(path, url):
    try:
        pull(url, path)
    except IOError:
        clone(url, path)
