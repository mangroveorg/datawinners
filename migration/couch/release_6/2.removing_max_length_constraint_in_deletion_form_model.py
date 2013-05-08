import traceback
import urllib2
from mangrove.contrib.deletion import ENTITY_DELETION_FORM_CODE
from mangrove.datastore.database import get_db_manager
from mangrove.form_model.form_model import get_form_model_by_code
from datetime import datetime
from migration.couch.utils import init_migrations, mark_start_of_migration, should_not_skip

log_file = open('migration_release_6_2.log', 'a')

SERVER = 'http://localhost:5984'

init_migrations('dbs_migrated_release_6_2.csv')

def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)

db_names = all_db_names(SERVER)

def log_statement(statement, db=""):
    print '%s:%s:%s\n' % (datetime.utcnow(), db, statement)
    log_file.writelines('%s:%s:%s\n' % (datetime.utcnow(), db, statement))


def migrate_db(db):
    try:
        mark_start_of_migration(db)
        manager = get_db_manager(server=SERVER, database=db)
        log_statement("Database: %s" % manager.database)
        form_model = get_form_model_by_code(manager, ENTITY_DELETION_FORM_CODE)
        log_statement("FormModel:%s" % form_model.id, manager.database)
        for field in form_model.fields:
            if field.code == 's':
                field.set_constraints([])
        form_model.save()
    except Exception as e:
        log_statement(":Error", db)
        traceback.print_exc(file=log_file)

def migrate_story_1924():

    log_statement("Start: Removing maxlength constraint from DeletionFormModel")
    for db in db_names:
        if should_not_skip(db):
            migrate_db(db)
    log_statement("End: Removing maxlength constraint from DeletionFormModel")

migrate_story_1924()