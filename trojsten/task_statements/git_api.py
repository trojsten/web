# -*- coding: utf-8 -*-
import os
import subprocess


class GitCommandError(Exception):
    """ Thrown if execution of the git command fails with non-zero status code. """
    def __init__(self, command, status, stderr=None):
        self.stderr = stderr
        self.status = status
        self.command = command

    def __str__(self):
        return (
            '\'%s\' returned exit status %i: %s' % (
                ' '.join(str(i) for i in self.command),
                self.status, self.stderr,
            )
        )


def run_git_command(command):
    ret = subprocess.call(command)
    if ret != 0:
        raise GitCommandError(' '.join(command), ret)


def clone(path, url):
    command = ['git', 'clone', path, url]
    run_git_command(command)


def pull(path):
    if not os.path.exists(path):
        raise IOError('Path does not exist: %s' % path)
    command = ['git', 'pull', '--git-dir=%s' % path]
    run_git_command(command)


def pull_or_clone(path, url):
    try:
        pull(path)
    except IOError:
        clone(path, url)
