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


def should_create_revisions(form_model, revision_ids, revision_number):
    revision_number = revision_number - 1
    for revision in revision_ids[1:]:
        revision_id = str(revision_number) + '-' + revision
        if revision_id not in form_model.snapshots.keys():
            return True
        revision_number = revision_number - 1
    return False


def migrate(database):
    try:
        log_statement("database: %s" % database)
        dbm = get_db_manager(SERVER, database=database)
        results = dbm.database.query(map_form_model_for_subject_questionnaires)
        for row in results:
            revision_dict = get_revisions_dict(database, row)
            log_statement("Form Model _id : %s " % row['key'])
            form_model = get_form_model(dbm, row['value'])
            revision_number = revision_dict['start']
            if should_create_revisions(form_model, revision_dict['ids'], revision_number):
            #The topmost id will be the current revision id of the document.
                for revision in revision_dict['ids']:
                    revision_id = str(revision_number) + '-' + str(revision)
                    log_statement("Existing Revisions : %s" % form_model.snapshots.keys())
                    if revision_id not in form_model.snapshots.keys():
                        revision_doc = urllib2.urlopen(
                            SERVER + "/" + database + "/" + row['key'] + "?rev=" + revision_id).read()
                        revision_doc = get_form_model(dbm, json.decode(revision_doc))
                        form_model._snapshots[revision_id] = revision_doc.fields
                        log_statement('%s : %s ' % (revision_id, revision_doc.fields))
                        log_statement("added revision: %s" % revision_id)
                    revision_number -= 1
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
    doc = urllib2.urlopen(SERVER + "/" + database + "/" + row['key'] + "?revs=true").read()
    doc = json.decode(doc)
    return doc.get('_revisions')


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