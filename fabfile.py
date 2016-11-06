import os
import time

from fabric.api import env
from fabric.operations import get, run, sudo
from fabric.context_managers import cd, prefix

"""
Fabric deployment scripts for github.com:trojsten/web

Notes:
 - Use $HOME/.ssh/config file to configure username for connecting to inteligent.trojsten.sk
"""

env.project_name = 'trojstenweb'
env.use_ssh_config = True
env.roledefs = {
    'prod': {
        'hosts': ['trojstenweb@archiv.ksp.sk'],
        'project_path': '/home/trojstenweb/web',
        'virtualenv_name': 'trojstenweb',
        'db_name': 'trojstenweb',
        'use_sudo': False,
        'server_configuration': 'trojsten/*.wsgi',
        'local': False,
    },
    'beta': {
        'hosts': ['inteligent.trojsten.sk:22100'],
        'project_path': '/usr/local/www/trojstenweb/web',
        'virtualenv_name': 'trojstenweb',
        'db_name': 'trojstenweb',
        'use_sudo': True,
        'sudo_user': 'trojstenweb',
        'shell': '/usr/local/bin/bash -l -c',
        'server_configuration': '/usr/local/www/trojstenweb/*.yaml',
        'local': False,
    },
    'local': {
        'user': os.environ.get('USER'),
        'hosts': ['localhost'],
        'project_path': os.path.dirname(os.path.realpath(__file__)),
        'virtualenv_name': 'trojstenweb',
        'db_name': 'trojsten',
        'use_sudo': False,
        'local': True,
    }
}


def srun(*args, **kwargs):
    if env.use_sudo:
        sudo(user=env.sudo_user, *args, **kwargs)
    else:
        run(*args, **kwargs)


def load_role(role_name):
    for k, v in env.roledefs[role_name].iteritems():
        env[k] = v


def local():
    load_role('local')


def beta():
    load_role('beta')


def prod():
    load_role('prod')


def pull():
    with cd(env.project_path):
        srun('git pull')


def collectstatic():
    manage('collectstatic', '--noinput')


def migrate():
    manage('migrate', '--noinput')


def load_fixtures():
    manage('loaddata', 'fixtures/*')


def install_requirements():
    with cd(env.project_path):
        with prefix('workon %s' % env.virtualenv_name):
            srun('pip install -r requirements.txt --exists-action w')
            if env.local:
                run('pip install -r requirements.devel.txt')


def manage(*args):
    with cd(env.project_path):
        with prefix('workon %s' % env.virtualenv_name):
            srun('python manage.py ' + ' '.join(args))


def restart_wsgi():
    with cd(env.project_path):
        srun('touch {}'.format(env.server_configuration))


def compile_translations():
    with prefix('workon %s' % env.virtualenv_name):
        with cd(env.project_path):
            srun('cd trojsten && python ../manage.py compilemessages')


def write_version_txt():
    with cd(env.project_path):
        srun('git log --no-merges --pretty=format:"%h %cd" -n 1 --date=short > version.txt')
        srun('echo >> version.txt')


def enable_maintenance_mode():
    srun('touch ~/maintenance')


def disable_maintenance_mode():
    srun('rm -f ~/maintenance')


def dump_sql():
    srun('mkdir -p db-dumps')
    filename = str(int(time.time()))
    with cd('db-dumps'):
        srun('pg_dump -Fc -O -c %s > %s.sql' % (env.db_name, filename))
        srun('rm -f latest.sql')
        srun('ln -s %s.sql latest.sql' % filename)


def get_latest_dump():
    srun('mkdir -p db-dumps')
    with cd('db-dumps'):
        get('latest.sql')


def freeze_results(*args):
    with cd(env.project_path):
        with prefix('workon %s' % env.virtualenv_name):
            srun('python manage.py freeze_results ' + ' '.join(args))


def branch(name):
    with cd(env.project_path):
        srun('git fetch')
        srun('git checkout %s' % name)


def after_pull():
    install_requirements()
    migrate()
    compile_translations()


def update():
    if not env.local:
        enable_maintenance_mode()
    pull()
    after_pull()
    if not env.local:
        collectstatic()
        restart_wsgi()
        disable_maintenance_mode()
    write_version_txt()


def version():
    with cd(env.project_path):
        srun('cat version.txt')
