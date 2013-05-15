#Change the unique id in the older entity registration form model. Change the instruction
import sys
import traceback

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

from datetime import datetime
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration, all_db_names
from datawinners import  settings

SERVER = 'http://localhost:5984'
credentials = settings.COUCHDBMAIN_CREDENTIALS

log_file = open('/var/log/datawinners/migration_release_7_1.log', 'a')
init_migrations('/var/log/datawinners/dbs_migrated_release_7_1.csv')

db_names = all_db_names(SERVER)

# excluding the following
# doc.form_code != 'reg' - to ignore the registration form model
# doc.form_code != 'delete' - to ignore the deletion form model
map_form_model_questionnaire = """
function(doc) {
   if (doc.document_type == 'FormModel' && doc.form_code != 'reg'
       && doc.form_code != 'delete' && doc.is_registration_model != true
       && !doc.void) {
            emit(doc.form_code,doc)
   }
}"""

def get_form_model(manager, questionnaire):
    doc = FormModelDocument.wrap(questionnaire['value'])
    form_model = FormModel.new_from_doc(manager, doc)
    return form_model


def migrate_form_model(form_model):
    form_model.create_snapshot()
    for field in form_model.fields:
        field.set_required(True)
    form_model.save()


def any_field_is_optional_in(form_model):
    for field in form_model.fields:
        if not field.is_required():
            return True
    return False


def migrate_db(database):
    log_statement(
        '\nStart migration on database : %s \n' % database)
    try:
        manager = get_db_manager(server=SERVER, database=database, credentials=credentials)
        questionnaire_form_model_docs = manager.database.query(map_form_model_questionnaire)
        mark_start_of_migration(database)
        for form_model_doc in questionnaire_form_model_docs:
            form_model = get_form_model(manager, form_model_doc)
            log_statement(
                "Process on :form_model document_id : %s , form code : %s" % (form_model.id, form_model.form_code))
            if any_field_is_optional_in(form_model):
                migrate_form_model(form_model)
                log_statement("Form Model updated :%s %s" % (database, form_model.form_code))
            log_statement(
                "End process on :form_model document_id : %s , form code : %s" % (form_model.id, form_model.form_code))
        log_statement(
            '\nEnd migration on database : %s\n' % database)
    except Exception as e:
        log_statement('error:%s:%s\n' % (e.message, database))
        traceback.print_exc(file=log_file)


def migrate_bug_2004(all_db_names):
    print "start ...."
    log_statement(
        '\nStart ===================================================================================================\n')
    for database in all_db_names:
        try:
            if should_not_skip(database):
                migrate_db(database)
        except Exception as e:
            log_statement(":Error" + e.message)
            traceback.print_exc(file=log_file)
    log_statement(
        '\n End ====================================================================================================\n')
    print "Completed migration"


def log_statement(statement):
    print '%s : %s\n' % (datetime.utcnow(), statement)
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))

migrate_bug_2004(db_names)
