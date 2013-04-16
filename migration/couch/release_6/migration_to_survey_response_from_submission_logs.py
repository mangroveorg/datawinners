from datetime import datetime
import sys
import traceback
import urllib2
from mangrove.datastore.database import get_db_manager
from mangrove.transport.contract.submission import Submission

MAX_NUMBER_DOCS = 50
log_file = open('migration_release_6.log', 'a')
SERVER = 'http://localhost:5984'

def migrate_db(db, offset):
    db_failures = []
    try:
        dbm = get_db_manager(server=SERVER, database=db)
        log_statement('Database: %s' % db)
        reduced_result = dbm.view.submissionlog(reduce=True)
        if reduced_result:
            log_statement('Total number of submission %s' % reduced_result[0].value.get('count'))
        rows = dbm.view.submissionlog(reduce=False, skip=offset, limit=MAX_NUMBER_DOCS)

        while len(rows) > 0:
            log_statement('Start processing from offset : %s' % offset)
            for row in rows:
                submission = Submission.new_from_doc(dbm = dbm, doc=Submission.__document_class__.wrap(row['value']))
                log_statement('Submission id : %s' % submission.uuid)
                survey_response = submission.create_survey_response(dbm)
                log_statement('Created survey response id : %s' % survey_response.uuid)
            offset += MAX_NUMBER_DOCS
            rows = dbm.view.submissionlog(reduce=False, skip=offset, limit=MAX_NUMBER_DOCS)

        log_file.writelines(
            '\n=========================================================================================================\n')

    except Exception as exception:
        log_statement('Processing failed for  %s :\n ' % db)
        traceback.print_exc(file = log_file)
        db_failures.append(db)

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


def log_statement(statement):
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


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
