from datetime import datetime
import traceback
import requests
from datawinners import settings
from datawinners.accountmanagement.post_activation_events import create_feed_database
from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.transport.contract.survey_response import SurveyResponse
from migration.couch.release_7.migrate_response_to_feed import MigrateToFeed, ProjectNotFoundException
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration

BATCH_SIZE = 100
COUCHDBMAIN_SERVER = 'http://localhost:5984'
log_file = open('/var/log/datawinners/migration_release_7_0_1.log', 'a')
init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_1.csv')


def create_feed_doc(dbm, feed_dbm, survey_response):
    try:
        MigrateToFeed(dbm, feed_dbm).migrate(survey_response)
        log_statement('Successfully migrated survey_reponse_id : %s' % survey_response.id)
    except (ProjectNotFoundException, FormModelDoesNotExistsException) as exception:
        log_statement('db_name: %s , failed survey_response_id : %s, error : %s' % (
            dbm.database_name, survey_response.id, exception.message))
    except Exception as exception:
        log_statement('db_name: %s , failed survey_response_id : %s, error : %s' % (
            dbm.database_name, survey_response.id, exception.message))
        traceback.print_exc(file=log_file)


def migrate_db(db_name):
    mark_start_of_migration(db_name)
    dbm = get_db_manager(settings.COUCH_DB_SERVER, db_name)
    feed_dbm = create_feed_database(db_name)
    rows = dbm.database.iterview("undeleted_survey_response/undeleted_survey_response", BATCH_SIZE, reduce=False)
    for row in rows:
        survey_response = SurveyResponse.new_from_doc(dbm=dbm,
                                                      doc=SurveyResponse.__document_class__.wrap(row['value']))
        create_feed_doc(dbm, feed_dbm, survey_response)


def migrate_survey_response_to_feed(all_db_names):
    print "start ...."
    log_statement(
        '\nStart ===================================================================================================\n')
    for database in all_db_names:
        try:
            if should_not_skip(database):
                migrate_db(database)
        except Exception as e:
            log_statement("Failed Database: %s Error %s" % (database, e.message))
            traceback.print_exc(file=log_file)
    log_statement(
        '\n End ====================================================================================================\n')
    print "Completed migration"


def log_statement(statement):
    print '%s : %s\n' % (datetime.utcnow(), statement)
    log_file.writelines('%s : %s\n' % (datetime.utcnow(), statement))


def all_db_names(server, credentials):
    all_dbs = requests.get(server + "/_all_dbs", auth=credentials)
    return filter(lambda x: x.startswith('hni_'), all_dbs.json())


migrate_db('hni_psi-madagascar_qmx864597')
# db_names = all_db_names(COUCHDBMAIN_SERVER, (settings.COUCHDBMAIN_USERNAME, settings.COUCHDBMAIN_PASSWORD))

# print db_names