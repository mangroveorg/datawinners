from copy import copy
from datetime import datetime
import sys
import traceback
import urllib2
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.database import get_db_manager
from mangrove.transport import TransportInfo
from mangrove.transport.contract.submission import Submission
from mangrove.transport.contract.survey_response import SurveyResponse
from migration.couch.utils import init_migrations, mark_as_completed, should_not_skip

MAX_NUMBER_DOCS = 50
log_file = open('migration_release_6_1.log', 'a')
SERVER = 'http://localhost:5984'

init_migrations('dbs_migrated_release_6_1.csv')

def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


def log_success_summary(db, dbm, skipped_count, successfully_processed):
    log_statement('Completed Survey Response creation for : %s' % db)
    log_statement("Submissions Processed: %s" % successfully_processed)
    log_statement('Skipped submissions: %s' % skipped_count)
    log_statement('Created Response: %s' % (successfully_processed - skipped_count))
    reduced_result = dbm.view.submissionlog(reduce=True)
    if reduced_result:
        log_statement('Total number of submission %s' % reduced_result[0].value.get('count'))
    response_result = dbm.view.surveyresponse(reduce=True)
    if response_result:
        log_statement('Total Number of responses: %s' % response_result[0].value.get('count'))


def log_failure_summary(db, successfully_processed, skipped_count):
    log_statement('Failed at(db,successful_offset): %s, %s\n' % (db, successfully_processed))
    log_statement('Skipped submissions: %s' % skipped_count)
    traceback.print_exc(file=log_file)


def create_survey_response(dbm, form_codes, row):
    submission = Submission.new_from_doc(dbm=dbm, doc=Submission.__document_class__.wrap(row['value']))
    log_statement('Submission id : %s' % submission.uuid)
    if submission.form_code not in form_codes:
        survey_response = create_survey_response(submission, dbm)
        log_statement('Created survey response id : %s' % survey_response.uuid)
        return True
    else:
        log_statement('Skipping Creation of Survey Response.')
        return False

def create_survey_response(submission, dbm):
    response = SurveyResponse(dbm, TransportInfo(submission.channel, submission.source,
        submission.destination), form_code=submission.form_code, form_model_revision=submission.form_model_revision,
        values=copy(submission.values))
    response.create_migrated_response(submission.status, submission.errors, submission.is_void(), submission._doc.submitted_on,
    submission.test, submission.event_time, submission._doc.data_record_id)
    return response

def registration_form_model_codes(dbm):
    rows = dbm.view.registration_form_model_by_entity_type(include_docs=True)
    # Form code for Data sender registration
    form_codes = ['reg']
    if len(rows):
        for row in rows:
            doc = FormModelDocument.wrap(row['doc'])
            form_model = FormModel.new_from_doc(dbm, doc)
            form_codes.append(form_model.form_code)

    return form_codes


def refresh_survey_response_views(dbm):
    try:
        log_statement('Starting refresh of views')
        dbm.view.survey_response_for_activity_period(include_docs=False)
        log_statement('View Refreshed : survey_response_for_activity_period')

        dbm.view.survey_response_by_survey_response_id(include_docs=False)
        log_statement('View Refreshed : survey_response_by_survey_response_id')

        dbm.view.deleted_survey_response(include_docs=False)
        log_statement('View Refreshed : deleted_survey_response')

        dbm.view.success_survey_response(include_docs=False)
        log_statement('View Refreshed : success_survey_response')

        dbm.view.undeleted_survey_response(include_docs=False)
        log_statement('View Refreshed : undeleted_survey_response')

        dbm.view.web_surveyresponse(include_docs=False)
        log_statement('View Refreshed : web_surveyresponse')

        log_statement('All views refreshed')

    except Exception as e:
        log_statement('Refreshing of views failed.')
        traceback.print_exc(file=log_file)

map_all_survey_response = """
function(doc) {
  if(doc.document_type == 'SurveyResponse') {
 	 emit(doc._id, doc);
  }
}"""

def remove_all_survey_response_documents(manager) :
    log_statement('Start:Removing survey response docs...:%s' % manager.database)
    all_survey_response_docs = manager.database.query(map_all_survey_response)
    for sr_doc in all_survey_response_docs :
        log_statement('Removing %s' % sr_doc.id)
        manager.database.delete(sr_doc.value)
    log_statement('Done:Removing survey response docs...:%s' % manager.database)


def migrate_db(db, offset):
    db_failures = []
    successfully_processed = 0
    skipped_count = 0
    try:
        print db
        mark_as_completed(db)
        dbm = get_db_manager(server=SERVER, database=db)
        log_statement('Database: %s' % db)

        remove_all_survey_response_documents(dbm)

        rows = dbm.view.submissionlog(reduce=False, skip=successfully_processed + offset, limit=MAX_NUMBER_DOCS)
        registration_form_codes = registration_form_model_codes(dbm)

        while len(rows) > 0:
            log_statement('Starting process from offset: %s' % (successfully_processed + offset))
            for row in rows:
                skipped_count += 1 if not create_survey_response(dbm, registration_form_codes, row) else 0
                successfully_processed += 1
            rows = dbm.view.submissionlog(reduce=False, skip=successfully_processed + offset, limit=MAX_NUMBER_DOCS)

        log_success_summary(db, dbm, skipped_count, successfully_processed)
        refresh_survey_response_views(dbm)

    except Exception:
        db_failures.append(db)
        log_failure_summary(db, successfully_processed, skipped_count)

    log_file.writelines(
        '\n=========================================================================================================\n')

    return  db_failures


def migrate(dbs):
    ''' This migration is for all submission logs that are created when responses for a questionnaire
        are submitted. These do not include subject creation / data sender creation etc submission logs'''

    log_statement('Starting migration process ...... ')
    db_failures = []
    for db in dbs:
        if should_not_skip(db):
            db_failures.append(migrate_db(db, 0))

    if db_failures:
        log_statement('Failed DBs: %s' % db_failures)
        print('Failed DBs: %s' % db_failures)
    log_statement('Completed migration process ...... ')
    print('Completed migrations of submissions to survey responses')


def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)

#This is for the manual run and is supposed to be used from [workspace]/datawinners/datawinners after activating the
#virtual environment by running 'source [path of virtual env bin] activate' and using the format
# python ../migration/couch/release_6/1.migration_to_survey_response_from_submission_logs.py [db name] [offset]
# where offset - is the number of documents to skip when doing migration for that db.
arguments = sys.argv
if len(arguments) == 3:
    db_name = sys.argv[1].strip()
    offset = sys.argv[2].strip()
    migrate_db(db_name, int(offset))
else:
    migrate(all_db_names(SERVER))
