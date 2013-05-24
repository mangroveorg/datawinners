# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import getpass

from fabric.api import run, env
from fabric.context_managers import cd, settings
from fabric.operations import sudo
import os
from datetime import  datetime

DATAWINNERS = 'datawinners'
MANGROVE = 'mangrove'

TODAY_IN_UTC = str(datetime.utcnow().date()).replace('-', '')

ENVIRONMENT_CONFIGURATIONS = {
    "showcase": "showcase_local_settings.py",
    "test": "test_local_settings.py",
    "master": "showcase_local_settings.py",
    "beta": "local_settings.py",
    "production": "prod_local_settings.py",
    "ec2": "ec2_local_settings.py",
    "qa": "local_settings_qa.py",
    "qa_supreme": "local_settings_qa_supreme.py"
}

ENVIRONMENT_VES = {
    "showcase": "/home/mangrover/virtual_env/datawinner",
    "production": "/home/mangrover/ve",
    "ec2": "/home/mangrover/.virtualenvs/datawinners",
    "qa": "/home/twer/virtual_env/datawinner",
    "test": "/home/twer/virtual_env/datawinner",
    "qa_supreme": "/home/datawinners/virtual_env/datawinner",
    "beta": "/home/administrator/virtual_env/datawinner",
}

ENVIRONMENT_TOMCAT = {
    "showcase": "/home/mangrover/tomcat",
    "production": "/home/mangrover/tomcat7",
    "ec2": "/home/mangrover/tomcat7",
}

ENVIRONMENT_JENKINS_JOB = {
    MANGROVE: 'Mangrove-develop',
    DATAWINNERS: 'Datawinners'
}


def git_clone_datawinners_if_not_present(code_dir):
    if run("test -d %s" % code_dir).failed:
        run("git clone git://github.com/mangroveorg/datawinners.git %s" % code_dir)


def git_clone_mangrove_if_not_present(code_dir):
    if run("test -d %s" % code_dir).failed:
        run("git clone git://github.com/mangroveorg/mangrove.git %s" % code_dir)


def activate_and_run(virtual_env, command):
    run('source %s/bin/activate && %s' % (virtual_env, command))


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
    print 'server stopped...'


def start_servers():
    run("sudo /etc/init.d/uwsgi start")
    run("sudo /etc/init.d/nginx start")
    print 'server started..'


def set_mangrove_commit_sha(branch, mangrove_build_number):
    if mangrove_build_number == 'lastSuccessfulBuild':
        mangrove_build_number = run(
            "curl http://178.79.163.33:8080/job/Mangrove-%s/lastSuccessfulBuild/buildNumber" % (branch,))
    run("echo 'Checking the mangrove commit sha for build number %s'" % mangrove_build_number)
    run(
        "export MANGROVE_COMMIT_SHA=`curl -s http://178.79.163.33:8080/job/Mangrove-%s/%s/artifact/last_successful_commit_sha`" % (
            branch, mangrove_build_number))
    run("echo MANGROVE_COMMIT_SHA=$MANGROVE_COMMIT_SHA")


def set_datawinner_commit_sha(datawinner_build_number):
    if datawinner_build_number == 'lastSuccessfulBuild':
        datawinner_build_number = run("curl http://178.79.163.33:8080/job/Datawinners/lastSuccessfulBuild/buildNumber")
    run("echo 'Checking the datawinner commit sha for build number %s'" % datawinner_build_number)
    run(
        "export DATAWINNER_COMMIT_SHA=`curl -s http://178.79.163.33:8080/job/Datawinners/%s/artifact/last_successful_commit_sha`" % (
            datawinner_build_number))
    run("echo DATAWINNER_COMMIT_SHA=$DATAWINNER_COMMIT_SHA")


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


def check_out_datawinners_code(datawinner_build_number, datawinners_code_dir, branch, virtual_env):
    git_clone_datawinners_if_not_present(datawinners_code_dir)
    with cd(datawinners_code_dir):
        run("cd %s" % datawinners_code_dir)
        run("git reset --hard HEAD")
        sync_branch(branch)
        delete_if_branch_exists(datawinner_build_number)
        run("git checkout -b %s $DATAWINNER_COMMIT_SHA" % (datawinner_build_number, ))
        run("git checkout .")
        activate_and_run(virtual_env, "pip install -r requirements.pip")


def deploy(mangrove_build_number, datawinner_build_number, home_dir, virtual_env, branch="develop",
           environment="showcase"):
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
        check_out_datawinners_code(datawinner_build_number, datawinners_code_dir, branch, virtual_env)
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
    env.couch_db_service_name = 'couchdb'


def qa():
    env.user = "twer"
    env.hosts = ["10.18.2.237"]
    env.key_filename = ["/home/dw/.ssh/id_rsa"]
    env.warn_only = True


def qa_supreme():
    env.user = "datawinners"
    env.hosts = ["172.18.9.1"]
    env.key_filename = ["/home/datawinners/.ssh/id_rsa"]
    env.warn_only = True
    env.couch_db_service_name = 'couchdb'


def test():
    env.user = "twer"
    env.hosts = ["10.18.2.237"]
    env.key_filename = ["/Users/twer/.ssh/id_rsa"]
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
    env.couch_db_service_name = 'couchbase-server'


def beta():
    env.user = getpass.getuser()
    env.hosts = ["localhost"]
    env.key_filename = ["%s/.ssh/id_rsa" % os.getenv("HOME")]
    env.warn_only = True
    env.couch_db_service_name = 'couchdb'


def anonymous():
    run("uname -a")


def commit_sha_from_build_number(jenkins_job_name, build_number):
    if build_number == 'lastSuccessfulBuild':
        build_number = run(
            "curl http://178.79.163.33:8080/job/%s/lastSuccessfulBuild/buildNumber" % (jenkins_job_name,))
    print("Retrieving the commit sha for build number %s of jenkins job %s" % (build_number, jenkins_job_name,))
    commit_sha = run("curl -s http://178.79.163.33:8080/job/%s/%s/artifact/last_successful_commit_sha" % (
        jenkins_job_name, build_number))

    print("%s_commit_sha: %s" % (jenkins_job_name, commit_sha))
    return commit_sha


def _project_dir(code_dir, project_name):
    project_dir = os.path.join(code_dir, project_name)
    if run("test -d %s" % project_dir).failed:
        run('git clone git://github.com/mangroveorg/%s.git %s' % (project_name, project_dir))
    return project_dir


def checkout_project(context, project_name):
    run("git reset --hard HEAD")
    run("git checkout " + context.branch)
    run("git pull --rebase")
    if context.branch in ['develop', 'origin/develop']:
        start_point = commit_sha_from_build_number(ENVIRONMENT_JENKINS_JOB[project_name],
            context.build_numbers[project_name])
    else:
        start_point = context.branch
    run("git checkout -B %s %s" % (TODAY_IN_UTC, start_point))


def install_requirement(virtual_env):
    activate_and_run(virtual_env, "pip install -r requirements.pip")


def post_checkout_datawinners(virtual_env):
    install_requirement(virtual_env)


def post_checkout_mangrove(virtual_env):
    install_requirement(virtual_env)
    activate_and_run(virtual_env, "python setup.py develop")


def deploy_project(context, project_name, post_checkout_function):
    with cd(_project_dir(context.code_dir, project_name)):
        checkout_project(context, project_name)
        post_checkout_function(context.virtual_env)


def check_out_latest_custom_reports_code_for_production(code_dir):
    custom_reports_dir = _project_dir(code_dir, "custom_reports")

    with cd(custom_reports_dir):
        run("git reset --hard HEAD")
        run("git checkout develop")
        run("git pull origin develop")
        if not run("git branch -a|grep %s" % TODAY_IN_UTC).failed:
            run("git branch -D %s" % TODAY_IN_UTC)
        run("git checkout -b %s HEAD" % TODAY_IN_UTC)
        run("git checkout .")


def _make_sure_code_dir_exists(context):
    run('mkdir -p %s' % context.code_dir)


def replace_setting_file_for_environment(environment):
    run("cp %s local_settings.py" % ENVIRONMENT_CONFIGURATIONS[environment])


def restart_couchdb():
    sudo("/etc/init.d/%s restart" % env.couch_db_service_name , pty=False)


def migrate_couchdb(context):
    if context.couch_migration_file:
        with cd('%s/datawinners' % context.code_dir):
            activate_and_run(context.virtual_env, "python %s" % context.couch_migration_file)

    if context.couch_migrations_folder:
        with cd('%s/datawinners/%s' % (context.code_dir, context.couch_migrations_folder)):
            migration_files = run('ls').split()
            with cd('%s/datawinners' % context.code_dir):
                for migration in migration_files:
                    if not (migration.__contains__('.log') or migration.__eq__('__init__.py')):
                        restart_couchdb()
                        print 'Running migration: %s' % migration
                        activate_and_run(context.virtual_env,
                            "python %s/%s" % (context.couch_migrations_folder, migration))
                        print 'Migration: %s complete' % migration


def link_repo(context, link_name):
    run('rm -f %s' % link_name)
    run('ln -s %s %s' % (os.path.join(context.code_dir, link_name), link_name))


def _deploy_mangrove(context):
    deploy_project(context, MANGROVE, post_checkout_mangrove)
    link_repo(context, MANGROVE)


def _deploy_datawinners(context):
    deploy_project(context, DATAWINNERS, post_checkout_datawinners)

    with cd(os.path.join(context.code_dir, DATAWINNERS, DATAWINNERS)):
        replace_setting_file_for_environment(context.environment)
        activate_and_run(context.virtual_env, "python manage.py migrate")
        activate_and_run(context.virtual_env, "python manage.py compilemessages")
        activate_and_run(context.virtual_env, "python manage.py syncviews syncall")

    migrate_couchdb(context)
    link_repo(context, DATAWINNERS)


class Context(object):
    def __init__(self, mangrove_build_number, datawinner_build_number, code_dir, environment, branch_name, virtual_env,
                 couch_migration_file, couch_migrations_folder):
        self.build_numbers = {MANGROVE: mangrove_build_number, DATAWINNERS: datawinner_build_number}
        self.code_dir = code_dir
        self.environment = environment
        self.branch = branch_name
        self.virtual_env = virtual_env
        self.couch_migration_file = couch_migration_file
        self.couch_migrations_folder = couch_migrations_folder


def production_deploy(mangrove_build_number="lastSuccessfulBuild",
                      datawinner_build_number="lastSuccessfulBuild",
                      code_dir="/home/twer/workspace",
                      environment='beta',
                      branch_name='develop',
                      couch_migration_file=None,
                      couch_migrations_folder=None):
    stop_servers()
    virtual_env = ENVIRONMENT_VES[environment]
    context = Context(mangrove_build_number, datawinner_build_number, code_dir, environment, branch_name, virtual_env,
        couch_migration_file, couch_migrations_folder)

    _make_sure_code_dir_exists(context)

    _deploy_mangrove(context)
    _deploy_datawinners(context)

    remove_cache(context)
#    start_servers()


def custom_reports_deploy(code_dir, environment='showcase'):
    check_out_latest_custom_reports_code_for_production(code_dir)

    with cd('%s/bin/' % ENVIRONMENT_TOMCAT[environment]):
        run('./catalina.sh stop')

    with cd('%s/webapps/birt-viewer/' % ENVIRONMENT_TOMCAT[environment]):
        run('rm crs')
        run('ln -s %s/custom_reports/crs/ crs' % code_dir)

    with cd('%s/bin/' % ENVIRONMENT_TOMCAT[environment]):
        run('./catalina.sh start')


def deploy_to_qa():
    production_deploy(code_dir="/home/twer/workspace", environment="qa")


def test_deploy_against_qa_machine():
    production_deploy(code_dir="/home/twer/workspace_for_script_test", branch_name="origin/release", environment="test")


def remove_cache(context):
    with cd(os.path.join(context.code_dir, DATAWINNERS, DATAWINNERS, 'media')):
        run('rm -rf CACHE/js/*')
        run('rm -rf CACHE/css/*')


def run_func_tests(environment="qa_supreme"):
    virtual_env = ENVIRONMENT_VES[environment]
    activate_and_run(virtual_env, "true")
    run("cd workspace/datawinners")
    run("./build.sh ft")
