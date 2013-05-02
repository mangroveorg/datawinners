from collections import OrderedDict
from datetime import datetime
import traceback
import urllib2
from couchdb import json
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.database import get_db_manager
from utils import init_migrations, mark_start_of_migration, should_not_skip

log_file = open('migration_release_6_4.log', 'a')
SERVER = 'http://localhost:5984'

init_migrations('dbs_migrated_release_6_4.csv')

def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)


def should_create_revisions(form_model, revision_ids):
    for revision_id in revision_ids[1:]:
        if revision_id not in form_model.snapshots.keys():
            return True
    return False


def migrate(database):
    try:
        log_statement("database: %s" % database)
        dbm = get_db_manager(SERVER, database=database)
        results = dbm.database.query(map_form_model_for_subject_questionnaires)
        for row in results:
            revision_ids = get_revisions_dict(database, row)
            log_statement("Form Model _id : %s " % row['key'])
            form_model = get_form_model(dbm, row['value'])
            if should_create_revisions(form_model, revision_ids):
            #The topmost id will be the current revision id of the document.
                log_statement("Existing Revisions : %s" % form_model.snapshots.keys())
                for revision_id in revision_ids:
                    if revision_id not in form_model.snapshots.keys():
                        revision_doc = urllib2.urlopen(
                            SERVER + "/" + database + "/" + row['key'] + "?rev=" + revision_id).read()
                        revision_doc = get_form_model(dbm, json.decode(revision_doc))
                        form_model._snapshots[revision_id] = revision_doc.fields
                        log_statement("added revision: %s" % revision_id)
                form_model.save()
        log_statement("Completed Database : %s" % database)
        mark_start_of_migration(database)
        log_file.writelines(
            "\n=======================================================\n")
    except Exception:
        log_statement("Failed Database : %s" % database)
        traceback.print_exc(file=log_file)


def get_form_model(manager, raw_str):
    doc = FormModelDocument.wrap(raw_str)
    form_model = FormModel.new_from_doc(manager, doc)
    return form_model


def get_revisions_dict(database, row):
    doc = urllib2.urlopen(SERVER + "/" + database + "/" + row['key'] + "?revs_info=true").read()
    doc = json.decode(doc)
    result = []
    for dictionary in doc.get('_revs_info'):
        if (dictionary.get('status') == "available"):
            result.append(dictionary.get('rev'))
    return result


def migrate_all():
    for database in all_db_names(SERVER):
        if should_not_skip(database):
            migrate(database)


map_form_model_for_subject_questionnaires = """
function(doc) {
   if (doc.document_type == 'FormModel'&& doc.form_code != 'reg'
       && doc.form_code != 'delete' && doc.entity_type[0] != 'reporter'
       && !doc.void) {

       for (var i in doc.json_fields){
           var field = doc.json_fields[i]
           if (field.entity_question_flag == true){
               emit(doc._id, doc);
           }
       }
   }
}"""

migrate_all()