import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from datawinners.feeds.migrate import FeedBuilder
from migration.couch.utils import mark_start_of_migration, all_db_names, migrate


def migrate_survey_response_to_feed(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info("Starting migration")
        mark_start_of_migration(db_name)
        FeedBuilder(db_name, logger).migrate_db()
    except Exception as e:
        logger.exception("FAILED")


migrate(all_db_names(), migrate_survey_response_to_feed, version=(7, 0, 3))

