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


def restart_servers():
    stop_servers()
    start_servers()


def stop_servers():
    run("sudo service uwsgi stop")
    run("sudo service nginx stop")


def start_servers():
    run("sudo service uwsgi start")
    run("sudo service nginx start")


def deploy(build_number, home_dir, virtual_env, environment="test", branch="master"):
    """build_number : hudson build number to be deployed
       home_dir: directory where you want to deploy the source code
       virtual_env : path to your virtual_env folder
    """
    if build_number == 'lastSuccessfulBuild':
        build_number = run("curl http://178.79.163.33:8080/job/Mangrove-%s/lastSuccessfulBuild/buildNumber" % (branch,))
    
    ENVIRONMENT_CONFIGURATIONS = {
        "showcase": "local_settings_showcase.py",
        "test": "local_settings_test.py",
        "master": "local_settings_showcase.py",
        "beta": "local_settings.py"
    }

    run("export COMMIT_SHA=`curl http://178.79.163.33:8080/job/Mangrove-%s/%s/artifact/last_successful_commit_sha`" % (
    branch, build_number))

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
            activate_and_run(virtual_env, "python manage.py migrate")
            activate_and_run(virtual_env, "python manage.py recreatedb")
            activate_and_run(virtual_env, "python manage.py compilemessages")
            restart_servers()


def showcase():
    env.user = "mangrover"
    env.hosts = ["178.79.161.90"]
    env.key_filename = ["/home/mangrover/.ssh/id_rsa"]
