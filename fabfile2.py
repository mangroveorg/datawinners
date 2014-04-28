# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import os
from datetime import datetime

from fabric.api import run, env
from fabric.context_managers import cd
from fabric.operations import sudo

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
    run("sudo service celeryd stop || echo 'celeryd already stopped'")
    print 'server stopped...'


def start_servers():
    run("sudo service uwsgi start")
    run("sudo service nginx start")
    run("sudo service celeryd start")
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
    run('sudo rm -rf '+ virtual_env +'/src/mangrove')
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

def restart_scheduler():
    sudo("/etc/init.d/reminders restart")

def restart_memcache():
    sudo("service memcached restart")

def restart_celery():
    sudo("service celeryd restart")


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
        restart_celery()
        activate_and_run(context.virtual_env, "python manage.py syncviews syncall")
        activate_and_run(context.virtual_env, "python manage.py syncfeedviews syncall")

    restart_memcache()
    migrate_couchdb(context)
    restart_memcache()
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


def take_psql_dump(backup_path, name_prefix):
    backup_name = "psql_backup_" + name_prefix + ".gz"
    run('pg_dump mangrove | gzip > %s/%s' % (backup_path, backup_name))


def take_couchdbmain_dump(couchdb_path, backup_path, name_prefix):
    backup = "mangrove_couchdb_main_backup_" + name_prefix + ".tar.gz"
    with cd(couchdb_path):
        run('sudo tar -czvPf  %s/%s  couchdbmain' % (backup_path, backup))

def take_couchdbfeed_dump(couchdb_path, backup_path, name_prefix):
    backup_name = "mangrove_couchdb_feed_backup_" + name_prefix + ".tar.gz"
    with cd(couchdb_path):
        run('sudo tar -czvPf  %s/%s couchdbfeed' % (backup_path, backup_name))


def take_elastic_search_index_dump(backup_path, name_prefix):
    backup_name = "mangrove_elasticsearch_index_backup_" + name_prefix + ".tar.gz"
    with cd('/var/lib/elasticsearch'):
        index_files = run('ls').split()
        run('sudo tar -czvPf %s/%s %s' % (backup_path, backup_name, index_files[0]))


def take_database_backup(backup=False):
    if backup == 'true':
        couchdb_path = '/opt/apache-couchdb/var/lib'
        today = datetime.now()
        backup_prefix = today.strftime("%d-%m-%Y")
        backup_path = "/home/mangrover/db_backup"+backup_prefix
        run('mkdir -p %s'%backup_path)
        take_psql_dump(backup_path, backup_prefix)
        take_couchdbmain_dump(couchdb_path, backup_path, backup_prefix)
        take_couchdbfeed_dump(couchdb_path, backup_path, backup_prefix)
        take_elastic_search_index_dump(backup_path, backup_prefix)


def production_deploy(mangrove_build_number="lastSuccessfulBuild",
                      datawinner_build_number="lastSuccessfulBuild",
                      code_dir="/home/mangrover/workspace",
                      environment='showcase',
                      branch_name='develop',
                      couch_migration_file=None,
                      couch_migrations_folder=None,
                      backup=False
):
    stop_servers()
    virtual_env = ENVIRONMENT_VES
    context = Context(mangrove_build_number, datawinner_build_number, code_dir, environment, branch_name, virtual_env,
                      couch_migration_file, couch_migrations_folder)

    _make_sure_code_dir_exists(context)
    take_database_backup(backup)
    _deploy_datawinners(context)

    remove_cache(context)
    if context.environment == 'prod':
        restart_scheduler()
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


def apply_couchdb_backup(couchdb_dir, backup_file, type):
    with cd(couchdb_dir):
        if backup_file:
            run('sudo rm -rf %s', type)
            run('sudo tar -xvf %s' % backup_file)
            run('sudo chown -R couchdb:couchdb %s' % type)
        else:
            print "no backup file"


def get_backup_file(backup_dir, partial_file_name):
    with cd(backup_dir):
        backup_files = run('ls').split()
        for f in backup_files:
            if partial_file_name in f:
                return f
        return None


def apply_psql_bkp(backup_dir, backup_file):
    with cd(backup_dir):
        run('dropdb mangrove && createdb -T template_postgis mangrove')
        run('gunzip %s' % backup_file)
        pg_dump_name = backup_file.rstrip('.gz')
        run('psql mangrove < %s' % pg_dump_name)
        with cd('/home/mangrover/workspace/datawinners/datawinners'):
            run('&& python manage.py syncdb --noinput && python manage.py migrate && python manage.py loadshapes')


def apply_elasticsearch_backup(backup_dir, index_bkp_file):
    with cd('/var/lib/elasticsearch'):
        indices_path = run('find $PWD -type d -name *0').split()
        with cd(indices_path[0]):
            run('sudo mkdir tmp')
            with cd('tmp'):
                run('tar -xvf %s/%s' % (backup_dir, index_bkp_file))
                indices_backup_path = run('find $PWD -type d -name *indices').split()
                run('sudo mv %s ../'%indices_backup_path)
                print "applied"
                run('sudo rm -rf ../tmp/')
    with cd('/var/lib/elasticsearch'):
        run('sudo chown -R elasticsearch:elasticsearch *')


def restart_elasticsearch():
    run('sudo service elasticsearch restart')


def apply_backup(backup_dir):
    couchdbmain_bkp_file = get_backup_file(backup_dir, 'mangrove_couchdb_main')
    couchdb_path = '/opt/apache-couchdb/var/lib'
    apply_couchdb_backup(couchdb_path, couchdbmain_bkp_file, 'couchdbmain')
    couchdbfeed_bkp_file = get_backup_file(backup_dir, 'mangrove_couchdb_feed')
    apply_couchdb_backup(couchdb_path, couchdbfeed_bkp_file, 'couchdbfeed')
    psql_bkp_file = get_backup_file(backup_dir, 'psql_backup')
    apply_psql_bkp(backup_dir, psql_bkp_file)
    #index_bkp_file = get_backup_file(backup_dir, 'mangrove_elasticsearch_index_backup')
    #apply_elasticsearch_backup(backup_dir, index_bkp_file)
    restart_couchdb()
    restart_elasticsearch()
