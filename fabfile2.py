# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import os
<<<<<<< HEAD
from datetime import datetime
=======
from datetime import  datetime
>>>>>>> 8_0_release

from fabric.api import run, env
from fabric.context_managers import cd
from fabric.operations import sudo
<<<<<<< HEAD
=======

>>>>>>> 8_0_release

DATAWINNERS = 'datawinners'
MANGROVE = 'mangrove'
couch_db_main_service_name = 'couchdbmain'
couch_db_feed_service_name = 'couchdbfeed'

ENVIRONMENT_CONFIGURATIONS = {
    "prod": "../../datawinners-conf/datawinners/local_settings_ec2.py",
}

ENVIRONMENT_VES = "/home/mangrover/virtual_env/datawinners"

ENVIRONMENT_TOMCAT = "/home/mangrover/tomcat7"


def activate_and_run(virtual_env, command):
    run('source %s/bin/activate && %s' % (virtual_env, command))


def restart_servers():
    stop_servers()
    start_servers()


def stop_servers():
    run("sudo service nginx stop || echo 'nginx already stopped'")
    run("sudo service uwsgi stop || echo 'uwsgi already stopped'")
    print 'server stopped...'


def start_servers():
    run("sudo service uwsgi start")
    run("sudo service nginx start")
    print 'server started..'


def showcase():
    env.user = "mangrover"
    env.hosts = ["184.72.223.168"]
    env.key_filename = ["/home/jenkins/.ssh/id_rsa"]
    env.warn_only = True


def qa():
    env.user = "datawinners"
    env.hosts = ["172.18.9.6"]
    env.key_filename = ["/home/datawinners/.ssh/id_rsa"]
    env.warn_only = True


def local():
    env.user = "mangrover"
    env.hosts = ["127.0.0.1"]
    env.key_filename = ["/home/jenkins/.ssh/id_rsa"]


def prod():
    env.user = "mangrover"
    env.hosts = ["54.243.31.50"]
    env.key_filename = ["/home/jenkins/.ssh/id_rsa"]
    env.warn_only = True


def anonymous():
    run("uname -a")


def _project_dir(code_dir, project_name):
    project_dir = os.path.join(code_dir, project_name)
    if run("test -d %s" % project_dir).failed:
        run('git clone git://github.com/mangroveorg/%s.git %s' % (project_name, project_dir))
    return project_dir


def checkout_project(context):
    run("git fetch -t")
    run("git checkout -f %s" % context.branch)


def post_checkout_datawinners(virtual_env):
    activate_and_run(virtual_env, "pip install -r requirements.pip")


def deploy_project(context, project_name, post_checkout_function):
    with cd(_project_dir(context.code_dir, project_name)):
        checkout_project(context)
        post_checkout_function(context.virtual_env)


def check_out_latest_custom_reports_code_for_production(code_dir):
    custom_reports_dir = _project_dir(code_dir, "custom_reports")
    TODAY_IN_UTC = str(datetime.utcnow().date()).replace('-', '')

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
    run("cp %s local_settings.py" % (
    ENVIRONMENT_CONFIGURATIONS.get(environment) or ("config/local_settings_" + environment + ".py")))


def restart_couchdb():
    sudo("/etc/init.d/%s restart" % couch_db_main_service_name, pty=False)
    sudo("/etc/init.d/%s restart" % couch_db_feed_service_name, pty=False)


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
                        #restart_couchdb()
                        print 'Running migration: %s' % migration
                        activate_and_run(context.virtual_env,
                                         "python %s/%s" % (context.couch_migrations_folder, migration))
                        print 'Migration: %s complete' % migration


def _link_repo(context, link_name):
    run('rm -f %s' % link_name)
    run('ln -s %s %s' % (os.path.join(context.code_dir, link_name), link_name))


def _checkout_datawinners_conf(code_dir):
    conf_project_name = "datawinners-conf"
    project_dir = os.path.join(code_dir, conf_project_name)
    run("rm -f %s" % project_dir)
    run('git clone git@github.com:hnidev/%s.git %s' % (conf_project_name, project_dir))


def _deploy_datawinners(context):
    if context.environment == "prod":
        _checkout_datawinners_conf(context.code_dir)
    deploy_project(context, DATAWINNERS, post_checkout_datawinners)

    with cd(os.path.join(context.code_dir, DATAWINNERS, DATAWINNERS)):
        replace_setting_file_for_environment(context.environment)
        activate_and_run(context.virtual_env, "python manage.py migrate")
        activate_and_run(context.virtual_env, "python manage.py compilemessages")
        activate_and_run(context.virtual_env, "python manage.py syncviews syncall")
        activate_and_run(context.virtual_env, "python manage.py syncfeedviews syncall")

    migrate_couchdb(context)
    _link_repo(context, DATAWINNERS)


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
                      code_dir="/home/mangrover/workspace",
                      environment='showcase',
                      branch_name='develop',
                      couch_migration_file=None,
                      couch_migrations_folder=None):
    stop_servers()
    virtual_env = ENVIRONMENT_VES
    context = Context(mangrove_build_number, datawinner_build_number, code_dir, environment, branch_name, virtual_env,
                      couch_migration_file, couch_migrations_folder)

    _make_sure_code_dir_exists(context)

    _deploy_datawinners(context)

    remove_cache(context)
    start_servers()


def custom_reports_deploy(code_dir, environment='showcase'):
    check_out_latest_custom_reports_code_for_production(code_dir)

    with cd('%s/bin/' % ENVIRONMENT_TOMCAT):
        run('./catalina.sh stop')

    with cd('%s/webapps/birt-viewer/' % ENVIRONMENT_TOMCAT):
        run('rm crs')
        run('ln -s %s/custom_reports/crs/ crs' % code_dir)

    with cd('%s/bin/' % ENVIRONMENT_TOMCAT):
        run('./catalina.sh start')


def remove_cache(context):
    with cd(os.path.join(context.code_dir, DATAWINNERS, DATAWINNERS, 'media')):
        run('rm -rf CACHE/js/*')
        run('rm -rf CACHE/css/*')


