from datetime import datetime
import traceback
import urllib2
from couchdb import json
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.database import get_db_manager
from mangrove.form_model.validation import TextLengthConstraint
from mangrove.transport.contract.survey_response import SurveyResponse
from migration.couch.utils import configure_csv, mark_as_completed, should_not_skip

log_file = open('migration_release_6_4.log', 'a')
SERVER = 'http://localhost:5984'

configure_csv('dbs_migrated_release_6_4.csv')

def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)


def should_create_revisions(form_model, revision_ids):
    if not form_model.snapshots:
        return False
    for revision_id in revision_ids[1:]:
        if revision_id not in form_model.snapshots.keys():
            return True
    return False


def is_max_len_equal_to(form_model, len):
    for field in form_model.fields:
        if field.is_entity_field:
            for constraint in field.constraints:
                if isinstance(constraint, TextLengthConstraint):
                    return len == constraint.max
    return False


def revsion_map(database, dbm):
    results = dbm.database.query(map_form_model_for_subject_questionnaires)
    revid_map = {}
    for row in results:
        revision_ids = get_revisions_dict(database, row)
        log_statement("Form Model _id : %s " % row['key'])
        form_model = get_form_model(dbm, row['value'])
        if is_max_len_equal_to(form_model, 20):
            rev_with_20 = form_model.revision
            for previous_rev in revision_ids:
                revision_doc = urllib2.urlopen(
                    SERVER + "/" + database + "/" + row['key'] + "?rev=" + previous_rev).read()
                revision_doc = get_form_model(dbm, json.decode(revision_doc))
                if is_max_len_equal_to(revision_doc, 12):
                    revid_map[previous_rev] = (rev_with_20, form_model.form_code)
                    log_statement("added revision for form:%s old:%s new:%s " % (form_model.form_code, previous_rev, rev_with_20))
                    break
                rev_with_20 = previous_rev
    return revid_map

map_survey_response_by_form_model_revision = """
function(doc) {
   if (doc.document_type == 'SurveyResponse' && doc.form_code == '%s' && doc.form_model_revision == '%s') {
               emit( doc._id, doc);
   }
}
"""

def migrate(database):
    try:
        log_statement("database: %s" % database)
        dbm = get_db_manager(SERVER, database=database)
        revid_map = revsion_map(database, dbm)
        for old_rev, values in revid_map.iteritems():
            survey_response_docs = dbm.database.query(map_survey_response_by_form_model_revision % (values[1], old_rev))
            for survey_response_doc in survey_response_docs :
                survey_response = SurveyResponse.new_from_doc(dbm=dbm, doc=SurveyResponse.__document_class__.wrap(survey_response_doc['value']))
                log_statement("Changing revision on:%s from:%s to:%s" % (survey_response.id, survey_response.form_model_revision, values[0]))
                survey_response.form_model_revision = values[0]
                survey_response.save()
        log_statement("Completed Database : %s" % database)
        mark_as_completed(database)
        log_file.writelines("\n=======================================================\n")
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
        if dictionary.get('status') == "available":
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
#migrate("hni_hni-madagascar_qua247294")
#migrate("hni_biggles-foundation_tip938359")
