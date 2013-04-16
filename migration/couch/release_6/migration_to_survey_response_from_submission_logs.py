from datetime import datetime
import sys
import traceback
import urllib2
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.database import get_db_manager
from mangrove.transport.contract.submission import Submission

MAX_NUMBER_DOCS = 50
log_file = open('migration_release_6.log', 'a')
SERVER = 'http://localhost:5984'

def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


def log_success_summary(dbm, skipped_count, successfully_processed):
    reduced_result = dbm.view.submissionlog(reduce=True)
    if reduced_result:
        log_statement('Total number of submission %s' % reduced_result[0].value.get('count'))
    response_result = dbm.view.surveyresponse(reduce=True)
    if response_result:
        log_statement('Total Number of responses: %s' % response_result[0].value.get('count'))
    log_statement("Submissions Processed: %s" % successfully_processed)
    log_statement('Skipped submissions: %s' % skipped_count)
    log_statement('Created Response: %s' % (successfully_processed - skipped_count))


def log_failure_summary(db, successfully_processed, skipped_count):
    log_statement('Failed at(db,successful_offset): %s, %s\n' % (db, successfully_processed))
    log_statement('Skipped submissions: %s' % skipped_count)
    traceback.print_exc(file=log_file)


def create_survey_response(dbm, form_codes, row):
    submission = Submission.new_from_doc(dbm=dbm, doc=Submission.__document_class__.wrap(row['value']))
    log_statement('Submission id : %s' % submission.uuid)
    if submission.form_code not in form_codes:
        survey_response = submission.create_survey_response(dbm)
        log_statement('Created survey response id : %s' % survey_response.uuid)
        return True
    else:
        log_statement('Skipping Creation of Survey Response.')
        return False


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


def migrate_db(db, offset):
    db_failures = []
    successfully_processed = 0
    skipped_count = 0

    try:
        dbm = get_db_manager(server=SERVER, database=db)
        log_statement('Database: %s' % db)
        rows = dbm.view.submissionlog(reduce=False, skip=successfully_processed + offset, limit=MAX_NUMBER_DOCS)
        registration_form_codes = registration_form_model_codes(dbm)

        while len(rows) > 0:
            log_statement('Starting process from offset: %s' % (successfully_processed + offset))
            for row in rows:
                skipped_count += 1 if not create_survey_response(dbm, registration_form_codes, row) else 0
                successfully_processed += 1
            rows = dbm.view.submissionlog(reduce=False, skip=successfully_processed + offset, limit=MAX_NUMBER_DOCS)

        log_success_summary(dbm, skipped_count, successfully_processed)
    except Exception as exception:
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
        db_failures.append(migrate_db(db, 0))

    if not db_failures:
        log_statement('Failed DBs: %s' % db_failures)
        print('Failed DBs: %s' % db_failures)
    log_statement('Completed migration process ...... ')
    print('Completed migrations of submissions to survey responses')


def all_db_names(server):
    all_dbs = urllib2.urlopen(server + "/_all_dbs").read()
    dbs = eval(all_dbs)
    return filter(lambda x: x.startswith('hni_'), dbs)

#This is for the manual run and is supposed to be used from [workspace]/datawinners/datawinners after activating the
#virtual environment by running 'source [path of virtual env bin] activate' and using the format
# python ../migration/couch/release_6/migration_to_survey_response_from_submission_logs.py [db name] [offset]
# where offset - is the number of documents to skip when doing migration for that db.
arguments = sys.argv
if len(arguments) == 3:
    db_name = sys.argv[1].strip()
    offset = sys.argv[2].strip()
    migrate_db(db_name, int(offset))
else:
    migrate(all_db_names(SERVER))
