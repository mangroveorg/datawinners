# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import getpass

from fabric.api import run, env
from fabric.context_managers import cd, settings
import os
from datetime import date

PROJECT_DIR = os.path.dirname(__file__)
ENVIRONMENT_CONFIGURATIONS = {
    "showcase": "showcase_local_settings.py",
    "test": "test_local_settings.py",
    "master": "showcase_local_settings.py",
    "beta": "local_settings.py",
    "production": "prod_local_settings.py",
    "ec2": "ec2_local_settings.py",
    "qa": "local_settings_qa.py"
}

ENVIRONMENT_VES = {
    "showcase": "/home/mangrover/ve",
    "production": "/home/mangrover/ve",
    "ec2": "/home/mangrover/.virtualenvs/datawinners",
    "qa": "/home/twer/virtual_env/datawinner"
}

ENVIRONMENT_TOMCAT = {
    "showcase": "/home/mangrover/tomcat",
    "production": "/home/mangrover/tomcat7",
    "ec2": "/home/mangrover/tomcat7",
}

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


def restart_servers():
    stop_servers()
    start_servers()


def stop_servers():
    run("sudo /etc/init.d/nginx stop")
    run("sudo /etc/init.d/uwsgi stop")


def start_servers():
    run("sudo /etc/init.d/uwsgi start")
    run("sudo /etc/init.d/nginx start")


def set_mangrove_commit_sha(branch, mangrove_build_number):
    if mangrove_build_number == 'lastSuccessfulBuild':
        mangrove_build_number = run(
            "curl http://178.79.163.33:8080/job/Mangrove-%s/lastSuccessfulBuild/buildNumber" % (branch,))
    run("echo 'Checking the mangrove commit sha for build number %s'" % mangrove_build_number)
    run("export MANGROVE_COMMIT_SHA=`curl -s http://178.79.163.33:8080/job/Mangrove-%s/%s/artifact/last_successful_commit_sha`" % (
            branch, mangrove_build_number))
    run("echo MANGROVE_COMMIT_SHA=$MANGROVE_COMMIT_SHA" )

def set_datawinner_commit_sha(datawinner_build_number):
    if datawinner_build_number == 'lastSuccessfulBuild':
        datawinner_build_number = run(
            "curl http://178.79.163.33:8080/job/Datawinners/lastSuccessfulBuild/buildNumber")
    run("echo 'Checking the datawinner commit sha for build number %s'" % datawinner_build_number)
    run("export DATAWINNER_COMMIT_SHA=`curl -s http://178.79.163.33:8080/job/Datawinners/%s/artifact/last_successful_commit_sha`" % (
            datawinner_build_number))
    run("echo DATAWINNER_COMMIT_SHA=$DATAWINNER_COMMIT_SHA" )

def check_out_mangrove_code(mangrove_build_number, mangrove_code_dir, branch, virtual_env):
    git_clone_mangrove_if_not_present(mangrove_code_dir)
    with cd(mangrove_code_dir):
        run("cd %s" % mangrove_code_dir)
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
        run("cd %s" % datawinners_code_dir)
        run("git reset --hard HEAD")
        sync_branch("develop")
        delete_if_branch_exists(datawinner_build_number)
        run("git checkout -b %s $DATAWINNER_COMMIT_SHA" % (datawinner_build_number, ))
        run("git checkout .")
        activate_and_run(virtual_env, "pip install -r requirements.pip")

def deploy(mangrove_build_number, datawinner_build_number, home_dir, virtual_env, branch="develop", environment="showcase"):
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
        check_out_datawinners_code(datawinner_build_number, datawinners_code_dir, virtual_env)
        with cd(datawinners_code_dir + '/datawinners'):
            run("cd %s/datawinners" % datawinners_code_dir)
            run("cp %s local_settings.py" % (ENVIRONMENT_CONFIGURATIONS[environment],))
            activate_and_run(virtual_env, "python manage.py syncdb --noinput")
            activate_and_run(virtual_env, "python manage.py migrate")
            activate_and_run(virtual_env, "python manage.py recreatedb")
            activate_and_run(virtual_env, "python manage.py compilemessages")
            activate_and_run(virtual_env, "python manage.py loadshapes")
            if environment == "test":
                restart_gunicorn(virtual_env)
            else:
                restart_servers()

def killfirefox():
    with settings(warn_only=True):
        run("killall firefox")

def showcase():
    env.user = "mangrover"
    env.hosts = ["178.79.161.90"]
    env.key_filename = ["/var/lib/jenkins/.ssh/id_rsa"]
    env.warn_only = True

def qa():
    env.user = "twer"
    env.hosts = ["10.18.2.237"]
    env.key_filename = ["/home/dw/.ssh/id_rsa"]
    env.warn_only = True

def local():
    env.user = "mangrover"
    env.hosts = ["127.0.0.1"]
    env.key_filename = ["/var/lib/jenkins/.ssh/id_rsa"]

def production():
    env.user = "mangrover"
    env.hosts = ["178.79.185.34"]
    env.key_filename = ["/var/lib/jenkins/.ssh/id_rsa"]
    env.warn_only = True

def ec2():
    env.user = "mangrover"
    env.hosts = ["54.243.31.50"]
    env.key_filename = ["/var/lib/jenkins/.ssh/id_rsa"]
    env.warn_only = True

def local_test():
    env.user = getpass.getuser()
    env.hosts = ["localhost"]
    env.key_filename = ["%s/.ssh/id_rsa" % os.getenv("HOME")]
    env.warn_only = True

def anonymous():
    run("uname -a")

def checkout_mangrove_to_production(code_dir, mangrove_build_number, virtual_env, branch='develop'):
    mangrove_job_name = 'Mangrove-develop'
    if mangrove_build_number == 'lastSuccessfulBuild':
        mangrove_build_number = run(
            "curl http://178.79.163.33:8080/job/%s/lastSuccessfulBuild/buildNumber" % (mangrove_job_name,))
    print("Checking the mangrove commit sha for build number %s" % mangrove_build_number)
    mangrove_commit_sha = run("curl -s http://178.79.163.33:8080/job/%s/%s/artifact/last_successful_commit_sha" % (mangrove_job_name, mangrove_build_number))
    print("mangrove_commit_sha: %s" % mangrove_commit_sha)

    if run("cd %s && ls | grep mangrove" % code_dir).failed:
        run('cd %s && git clone git://github.com/mangroveorg/mangrove.git' % code_dir)
    mangrove_dir = code_dir + '/mangrove'
    with cd(mangrove_dir):
        run("git reset --hard HEAD")
        run("git checkout develop")
        run("git pull origin develop")
        mangrove_branch = str(date.today()).replace('-', '')
        if not run("git branch -a|grep %s" % mangrove_branch).failed:
            run("git branch -D %s" % mangrove_branch)

        if branch in ['develop', 'origin/develop']:
            run("git checkout -b %s %s" % (mangrove_branch, mangrove_commit_sha))
            run("git checkout .")
        else:
            run("git checkout -b %s %s" % (mangrove_branch, branch))

        activate_and_run(virtual_env, "pip install -r requirements.pip")
        activate_and_run(virtual_env, "python setup.py develop")

def check_out_datawinners_code_for_production(code_dir, datawinner_build_number, virtual_env, branch):
    if datawinner_build_number == 'lastSuccessfulBuild':
        datawinner_build_number = run(
            "curl http://178.79.163.33:8080/job/Datawinners/lastSuccessfulBuild/buildNumber")
    print("Checking the datawinner commit sha for build number %s" % datawinner_build_number)
    datawinner_commit_sha = run("curl -s http://178.79.163.33:8080/job/Datawinners/%s/artifact/last_successful_commit_sha" % (
        datawinner_build_number))
    print("datawinner_commit_sha: %s" % datawinner_commit_sha)

    if run("cd %s && ls | grep datawinners" % code_dir).failed:
        run('cd %s && git clone git://github.com/mangroveorg/datawinners.git' % code_dir)
    datawinners_dir = code_dir + '/datawinners'
    with cd(datawinners_dir):
        datawinner_branch = str(date.today()).replace('-', '')
        run("git reset --hard HEAD")
        run("git fetch")
        run("git checkout develop")
        run("git pull origin develop")
        if not run("git branch -a|grep %s" % datawinner_branch).failed:
            run("git branch -D %s" % datawinner_branch)

        if branch in ['develop', 'origin/develop']:
            run("git checkout -b %s %s" % (datawinner_branch, datawinner_commit_sha))
            run("git checkout .")
        else:
            run("git checkout -b %s %s" % (datawinner_branch, branch))

        activate_and_run(virtual_env, "pip install -r requirements.pip")

def check_out_latest_custom_reports_code_for_production(code_dir):
    if run("cd %s && ls | grep custom_reports" % code_dir).failed:
        run('cd %s && git clone git://github.com/mangroveorg/custom_reports.git' % code_dir)
    custom_reports_dir = code_dir + '/custom_reports'
    with cd(custom_reports_dir):
        run("git reset --hard HEAD")
        run("git checkout develop")
        run("git pull origin develop")
        custom_reports_branch = str(date.today()).replace('-', '')
        if not run("git branch -a|grep %s" % custom_reports_branch).failed:
            run("git branch -D %s" % custom_reports_branch)
        run("git checkout -b %s HEAD" % custom_reports_branch)
        run("git checkout .")

def production_deploy(mangrove_build_number, datawinner_build_number, code_dir, environment = 'showcase', datawinner_branch='develop',
                      couch_migration_file=None):
    stop_servers()
    print 'server stopped...'
    if run('cd %s' % code_dir).failed:
        run('mkdir %s' % code_dir)
    print 'cd %s' % code_dir
    virtual_env = ENVIRONMENT_VES[environment]
    checkout_mangrove_to_production(code_dir, mangrove_build_number, virtual_env, datawinner_branch)
    check_out_datawinners_code_for_production(code_dir, datawinner_build_number, virtual_env, datawinner_branch)

    datawinners_dir = code_dir + '/datawinners/datawinners'
    print 'datawinner directory:', datawinners_dir
    with cd(datawinners_dir):
        print 'goto datawinner dir'
        run("cp %s local_settings.py" % ENVIRONMENT_CONFIGURATIONS[environment])
        activate_and_run(virtual_env, "python manage.py migrate")
        activate_and_run(virtual_env, "python manage.py compilemessages")
        activate_and_run(virtual_env, "python manage.py syncviews syncall")

    if couch_migration_file is not None:
        with cd('%s/datawinners' % code_dir):
            activate_and_run(virtual_env, "python %s" % couch_migration_file)

    if not run('cd mangrove').failed:
        run('rm mangrove')
    run('ln -s %s/mangrove/ mangrove' % code_dir)

    if not run('cd datawinners').failed:
        run('rm datawinners')
    run('ln -s %s/datawinners/ datawinners' % code_dir)

    remove_cache()
    start_servers()
    print 'server started..'

def custom_reports_deploy(code_dir, environment = 'showcase'):
    check_out_latest_custom_reports_code_for_production(code_dir)

    with cd('%s/bin/' % ENVIRONMENT_TOMCAT[environment]):
        run('./catalina.sh stop')

    with cd('%s/webapps/birt-viewer/' % ENVIRONMENT_TOMCAT[environment]):
#        if not run('cd crs').failed:
        run('rm crs')
        run('ln -s %s/custom_reports/crs/ crs' % code_dir)

    with cd('%s/bin/' % ENVIRONMENT_TOMCAT[environment]):
        run('./catalina.sh start')


def testRunFab():
    print "hello"

def deploy_to_qa():
    print 'start ...........'
    production_deploy(mangrove_build_number="lastSuccessfulBuild",
        datawinner_build_number="lastSuccessfulBuild",
        code_dir="/home/twer/workspace",
        environment="qa")

def remove_cache():
    with cd(os.path.join(PROJECT_DIR, 'datawinners/media/')):
        run('rm -rf CACHE/js/*')
        run('rm -rf CACHE/css/*')
