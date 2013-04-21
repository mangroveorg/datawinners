import urllib2
from mangrove.contrib.deletion import ENTITY_DELETION_FORM_CODE
from mangrove.datastore.database import get_db_manager
from mangrove.form_model.form_model import get_form_model_by_code
from datetime import datetime

log_file = open('migration_release_6_2.log', 'a')

SERVER = 'http://localhost:5984'

def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)

db_names = all_db_names(SERVER)

def log_statement(statement):
    print '%s : %s\n' % (datetime.utcnow(), statement)
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))

def migrate_story_1924():
    failed_managers = []
    log_statement("Start: Removing maxlength constraint from DeletionFormModel")
    for db in db_names:
        global manager
        try:
            manager = get_db_manager(server=SERVER, database=db)
            log_statement("Database: %s" % manager.database)
            try:
                form_model = get_form_model_by_code(manager, ENTITY_DELETION_FORM_CODE)
                log_statement("FormModel:%s" % form_model.id)
                for field in form_model.fields:
                    if field.code == 's':
                        field.set_constraints([])
                form_model.save()
            except Exception as e:
                log_statement("error:" + e.message)
        except Exception as e:
            failed_managers.append((manager, e.message))
    log_statement("End: Removing maxlength constraint from DeletionFormModel")

    log_statement('failed managers if any')
    for manager, exception_message in failed_managers:
        log_statement(" %s failed. the reason :  %s" % (manager, exception_message))

migrate_story_1924()