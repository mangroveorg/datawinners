from fabric.api import run
from fabric.context_managers import cd, settings

def git_clone_if_not_present(code_dir):
    if run("test -d %s" % code_dir).failed:
        run("git clone git://github.com/mangroveorg/mangrove.git %s" % code_dir)

def activate_and_run(virtual_env,command):
    run('source %s/bin/activate && ' % virtual_env + command)

def branch_exists(branch_name):
    return not run("git branch -a|grep %s" % branch_name).failed

def sync_develop_branch():
    run("git checkout develop")
    run("git pull origin develop")


def delete_if_branch_exists(build_number):
    if branch_exists(build_number):
        run("git branch -D %s" % build_number)


def deploy(build_number,home_dir,virtual_env):
    """build_number : hudson build number to be deployed
       home_dir: directory where you want to deploy the source code
       virtual_env : path to your virtual_env folder
    """
    run("export COMMIT_SHA=`curl http://hudson.mvpafrica.org:8080/job/Mangrove-develop/%s/artifact/last_successful_commit_sha`" % (build_number,))

    code_dir = home_dir+'/mangrove'
    with settings(warn_only=True):
        git_clone_if_not_present(code_dir)
        with cd(code_dir):
            sync_develop_branch()
            delete_if_branch_exists(build_number)
            run("git checkout -b %s $COMMIT_SHA" % (build_number,) )
            activate_and_run(virtual_env,"pip install -r requirements.pip")
        with cd(code_dir+'/src/datawinners'):
            activate_and_run(virtual_env,"python manage.py syncdb")

