# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from fabric.api import run, env
from fabric.context_managers import cd, settings
import os
import sys

PROJECT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(PROJECT_DIR, '../../src'))


def git_clone_if_not_present(code_dir):
    if run("test -d %s" % code_dir).failed:
        run("git clone git://github.com/mangroveorg/mangrove.git %s" % code_dir)


def activate_and_run(virtual_env, command):
    run('source %s/bin/activate && ' % virtual_env + command)


def branch_exists(branch_name):
    return not run("git branch -a|grep %s" % branch_name).failed


def sync_branch(branch):
    run("git pull")
    run("git checkout %s" % branch)
    run("git pull origin %s" % branch)


def delete_if_branch_exists(build_number):
    if branch_exists(build_number):
        run("git branch -D %s" % build_number)


def restart_gunicorn(virtual_env):
    if gunicorn_is_running():
        stop_gunicorn()
    start_gunicorn(virtual_env)


def gunicorn_is_running():
    return not run("pgrep gunicorn").failed


def stop_gunicorn():
    run("kill -9 `pgrep gunicorn`")


def start_gunicorn(virtual_env):
    activate_and_run(virtual_env, "gunicorn_django -D -b 0.0.0.0:8000 --pid=mangrove_gunicorn")


def deploy(build_number, home_dir, virtual_env, environment="test", branch="develop"):
    """build_number : hudson build number to be deployed
       home_dir: directory where you want to deploy the source code
       virtual_env : path to your virtual_env folder
    """
    ENVIRONMENT_CONFIGURATIONS = {
                                    "showcase": "showcase_local_settings.py",
                                    "test": "test_local_settings.py",
                                    "master": "showcase_local_settings.py"
                                 }

    if build_number == 'lastSuccessfulBuild':
        build_number = run("curl http://178.79.163.33:8080/job/Mangrove-%s/lastSuccessfulBuild/buildNumber" % (branch,))

    run("export COMMIT_SHA=`curl http://178.79.163.33:8080/job/Mangrove-%s/%s/artifact/last_successful_commit_sha`" % (branch,build_number))

    code_dir = home_dir + '/mangrove'
    with settings(warn_only=True):
        git_clone_if_not_present(code_dir)
        with cd(code_dir):
            run("git reset --hard HEAD")
            sync_branch(branch)
            delete_if_branch_exists(build_number)
            run("git checkout -b %s $COMMIT_SHA" % (build_number, ))
            run("git checkout .")
            activate_and_run(virtual_env, "pip install -r requirements.pip")
        with cd(code_dir + '/src/datawinners'):
            run("cp %s local_settings.py" % (ENVIRONMENT_CONFIGURATIONS[environment],))
            activate_and_run(virtual_env, "python manage.py syncdb --noinput")
            activate_and_run(virtual_env, "python manage.py recreatedb")
            restart_gunicorn(virtual_env)


def showcase():
    env.user = "mangrover"
    env.hosts = ["178.79.161.90"]
    env.key_filename = ["/home/mangrover/.ssh/id_dsa"]
