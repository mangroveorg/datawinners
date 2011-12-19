# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from fabric.api import run, env
from fabric.context_managers import cd, settings
import os
import sys

PROJECT_DIR = os.path.dirname(__file__)


def git_clone_datawinners_if_not_present(code_dir):
    if run("test -d %s" % code_dir).failed:
        run("git clone git://github.com/mangroveorg/datawinners.git %s" % code_dir)
        
def git_clone_mangrove_if_not_present(code_dir):
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


def set_mangrove_commit_sha(branch, mangrove_build_number):
    if mangrove_build_number == 'lastSuccessfulBuild':
        mangrove_build_number = run(
            "curl http://178.79.163.33:8080/job/Mangrove-%s/lastSuccessfulBuild/buildNumber" % (branch,))
    run(
        "export MANGROVE_COMMIT_SHA=`curl http://178.79.163.33:8080/job/Mangrove-%s/%s/artifact/last_successful_commit_sha`" % (
            branch, mangrove_build_number))
    
def set_datawinner_commit_sha(datawinner_build_number):
    if datawinner_build_number == 'lastSuccessfulBuild':
        datawinner_build_number = run(
            "curl http://178.79.163.33:8080/job/Datawinners/lastSuccessfulBuild/buildNumber")
    run(
        "export DATWINNER_COMMIT_SHA=`curl http://178.79.163.33:8080/job/Datawinners/%s/artifact/last_successful_commit_sha`" % (
            datawinner_build_number))

def check_out_mangrove_code(mangrove_build_number, mangrove_code_dir, branch, virtual_env):
    git_clone_mangrove_if_not_present(mangrove_code_dir)
    with cd(mangrove_code_dir):
        run("git reset --hard HEAD")
        sync_branch(branch)
        delete_if_branch_exists(mangrove_build_number)
        run("git checkout -b %s $MANGROVE_COMMIT_SHA" % (mangrove_build_number, ))
        run("git checkout .")
        activate_and_run(virtual_env, "pip install -r requirements.pip")
        activate_and_run(virtual_env, "python setup.py develop")
        
def check_out_datawinners_code(datawinner_build_number, datawinners_code_dir, virtual_env):
    git_clone_datawinners_if_not_present(datawinners_code_dir)
    with cd(datawinners_code_dir):
        run("git reset --hard HEAD")
        sync_branch("develop")
        delete_if_branch_exists(datawinner_build_number)
        run("git checkout -b %s $DATAWINNER_COMMIT_SHA" % (datawinner_build_number, ))
        run("git checkout .")
        activate_and_run(virtual_env, "pip install -r requirements.pip")

def deploy(mangrove_build_number, datawinner_build_number, home_dir, virtual_env, branch="develop"):
    """build_number : hudson build number to be deployed
       home_dir: directory where you want to deploy the source code
       virtual_env : path to your virtual_env folder
    """
    set_mangrove_commit_sha(branch, mangrove_build_number)
    set_datawinner_commit_sha(datawinner_build_number)
    
    mangrove_code_dir = home_dir + '/mangrove'
    datawinners_code_dir = home_dir + '/datawinners'
    with settings(warn_only=True):
        check_out_mangrove_code(mangrove_build_number, mangrove_code_dir, branch, virtual_env)
        check_out_datawinners_code(mangrove_build_number, mangrove_code_dir, virtual_env)
        with cd(datawinners_code_dir + '/datawinners'):
            activate_and_run(virtual_env, "python manage.py syncdb --noinput")
            activate_and_run(virtual_env, "python manage.py migrate")
            activate_and_run(virtual_env, "python manage.py recreatedb")
            activate_and_run(virtual_env, "python manage.py updatedb syncall")
            activate_and_run(virtual_env, "python manage.py compilemessages")
            restart_gunicorn(virtual_env)


def showcase():
    env.user = "mangrover"
    env.hosts = ["178.79.161.90"]
    env.key_filename = ["/home/mangrover/.ssh/id_dsa"]
