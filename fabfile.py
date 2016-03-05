from fabric.api import run, cd, prefix, env, get
import os
import time

PROJECT_PATH = '~/web'
LOCAL = False
DEFAULT_VIRTUALENV_NAME = 'trojstenweb'
VIRTUALENV_NAME = 'trojstenweb'
DB_NAME = 'trojsten'

def _reset_env():
    global PROJECT_PATH
    global LOCAL
    global VIRTUALENV_NAME
    LOCAL = False
    PROJECT_PATH = '~/web'
    VIRTUALENV_NAME = DEFAULT_VIRTUALENV_NAME

def beta():
    global DB_NAME
    _reset_env()
    env.user = 'betakspweb'
    env.hosts = ['archiv.ksp.sk']
    DB_NAME = 'betakspweb'

def prod():
    global DB_NAME
    _reset_env()
    env.user = 'trojstenweb'
    env.hosts = ['archiv.ksp.sk']
    DB_NAME = 'trojstenweb'

def local(venvname=DEFAULT_VIRTUALENV_NAME):
    global PROJECT_PATH
    global LOCAL
    global VIRTUALENV_NAME
    global DB_NAME
    env.user = os.environ.get('USER')
    env.hosts = ['localhost']
    PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
    LOCAL = True
    VIRTUALENV_NAME = venvname
    DB_NAME = 'trojsten'

def pull():
    with cd(PROJECT_PATH):
        run('git pull')

def collectstatic():
    manage('collectstatic', '--noinput')

def migrate():
    manage('migrate', '--noinput')

def load_fixtures():
    manage('loaddata', 'fixtures/*')

def install_requirements():
    with cd(PROJECT_PATH):
        with prefix('workon %s' % VIRTUALENV_NAME):
            run('pip install -r requirements.txt --exists-action w')
            if LOCAL:
                run('pip install -r requirements.devel.txt')

def manage(*args):
    with cd(PROJECT_PATH):
        with prefix('workon %s' % VIRTUALENV_NAME):
            run('python manage.py ' + ' '.join(args))

def restart_wsgi():
    with cd(PROJECT_PATH):
        run('touch trojsten/*.wsgi')

def compile_translations():
    with prefix('workon %s' % VIRTUALENV_NAME):
        with cd(PROJECT_PATH):
            run('cd trojsten && python ../manage.py compilemessages')

def write_version_txt():
    with cd(PROJECT_PATH):
        run('git log --no-merges --pretty=format:"%h %cd" -n 1 --date=short > version.txt')
        run('echo >> version.txt')

def enable_maintenance_mode():
    run('touch ~/maintenance')

def disable_maintenance_mode():
    run('rm -f ~/maintenance')

def dump_sql():
    run('mkdir -p db-dumps')
    filename = str(int(time.time()))
    with cd('db-dumps'):
        run('pg_dump -Fc -O -c %s > %s.sql' % (DB_NAME, filename))
        run('rm -f latest.sql')
        run('ln -s %s.sql latest.sql' % filename)

def get_latest_dump():
    run('mkdir -p db-dumps')
    with cd('db-dumps'):
        get('latest.sql')

def freeze_results(*args):
    with cd(PROJECT_PATH):
        with prefix('workon %s' % VIRTUALENV_NAME):
            run('python manage.py freeze_results ' + ' '.join(args))

def branch(name):
    with cd(PROJECT_PATH):
        run('git fetch')
        run('git checkout %s' % name)

def update():
    if not LOCAL:
        enable_maintenance_mode()
    pull()
    install_requirements()
    migrate()
    compile_translations()
    if not LOCAL:
        collectstatic()
        restart_wsgi()
        disable_maintenance_mode()
    write_version_txt()

def version():
    with cd(PROJECT_PATH):
        run('cat version.txt')
