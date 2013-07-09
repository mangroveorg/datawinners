import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from datawinners.feeds.migrate import FeedBuilder
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration, all_db_names, DWThreadPool

NUMBER_OF_THREADS = 12
init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_3.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_3.log', level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def create_feed_docs(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info("Starting migration")
        mark_start_of_migration(db_name)
        FeedBuilder(db_name, logger).migrate_db()
    except Exception as e:
        logger.exception("FAILED")


def migrate_survey_response_to_feed(all_db_names):
    pool = DWThreadPool(NUMBER_OF_THREADS, NUMBER_OF_THREADS)
    for db_name in all_db_names:
        if should_not_skip(db_name):
            pool.submit(create_feed_docs, db_name)

    pool.wait_for_completion()
    print "Completed!"


migrate_survey_response_to_feed(all_db_names())

