#Change the unique id in the older entity registration form model. Change the instruction

from datetime import datetime
import traceback
import urllib2
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import TextLengthConstraint
from migration.couch.utils import init_migrations, should_not_skip, mark_as_completed

SERVER = 'http://localhost:5984'
log_file = open('migration_release_6_3.log', 'a')

init_migrations('dbs_migrated_release_6_3.csv')

def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)

db_names = all_db_names(SERVER)

# excluding the following
# doc.form_code != 'reg' - to ignore the registration form model
# doc.form_code != 'delete' - to ignore the deletion form model
# doc.entity_type[0] != 'reporter' - to ignore summary reports
map_form_model_for_subject_questionnaires = """
function(doc) {
   if (doc.document_type == 'FormModel'&& doc.form_code != 'reg'
       && doc.form_code != 'delete' && doc.entity_type[0] != 'reporter'
       && !doc.void) {

       for (var i in doc.json_fields){
           var field = doc.json_fields[i]
           if (field.entity_question_flag == true && field.constraints[0][1]['max'] == 12){
               emit( doc.form_code, doc);
           }
       }
   }
}"""

def get_form_model(manager, questionnaire):
    doc = FormModelDocument.wrap(questionnaire['value'])
    form_model = FormModel.new_from_doc(manager, doc)
    return form_model


def migrate_db(database):
    log_statement(
        '\nStart migration on database : %s \n' % database)
    try:
        manager = get_db_manager(server=SERVER, database=database)
        subject_form_model_docs = manager.database.query(map_form_model_for_subject_questionnaires)
        mark_as_completed(database)
        for form_model_doc in subject_form_model_docs:
            form_model = get_form_model(manager, form_model_doc)
            log_statement(
                "Process on :form_model document_id : %s , form code : %s" % (form_model.id, form_model.form_code))
            for field in form_model.fields:
                if field.is_entity_field:
                    field.set_constraints([TextLengthConstraint(min=1, max=20)._to_json()])
            form_model.save()
            log_statement(
                "End process on :form_model document_id : %s , form code : %s" % (form_model.id, form_model.form_code))
        log_statement(
            '\nEnd migration on database : %s\n' % database)
    except Exception as e:
        log_statement('error:%s:%s\n' % (e.message, database))
        traceback.print_exc(file=log_file)

def migrate_story_2074(all_db_names):
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

migrate_story_2074(db_names)
