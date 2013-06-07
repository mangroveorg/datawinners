import logging
import requests
from datawinners.feeds.migrate import FeedBuilder
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration

COUCHDBMAIN_SERVER = 'http://localhost:5984'
log_file = open('/var/log/datawinners/migration_release_7_0_1.log', 'a')
init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_1.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_1.log', level=logging.DEBUG,
                    format="%(asctime)s;%(levelname)s;%(message)s")


def migrate_survey_response_to_feed(all_db_names):
    logging.info('\nStart ==========================================================================================\n')
    for database in all_db_names:
        try:
            if should_not_skip(database):
                mark_start_of_migration(database)
                FeedBuilder(database, logging.getLogger(__name__)).migrate_db()
        except Exception as e:
            logging.exception("Failed Database: %s Error %s" % (database, e.message))
    logging.info('\n End ===========================================================================================\n')


def all_db_names(server, credentials):
    all_dbs = requests.get(server + "/_all_dbs", auth=credentials)
    return filter(lambda x: x.startswith('hni_'), all_dbs.json())


FeedBuilder('hni_psi-madagascar_qmx864597', logging.getLogger(__name__)).migrate_db()
# db_names = all_db_names(COUCHDBMAIN_SERVER, (settings.COUCHDBMAIN_USERNAME, settings.COUCHDBMAIN_PASSWORD))

# print db_names