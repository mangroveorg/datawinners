import logging
from django.core.management import BaseCommand
from datawinners.feeds.migrate import FeedBuilder

logger = logging.getLogger(__name__)

def create_feed_for_survey_response(database_name, survey_response_id):
     FeedBuilder(database_name, logger).migrate_document(survey_response_id)


def create_feeds_for_database(database_name):
    FeedBuilder(database_name, logger).migrate_db()

class Command(BaseCommand):
    def handle(self, *args, **options):
        database_name = args[0]
        print "creating feed for database: " + database_name
        if len(args) > 1:
            for survey_response_id in args[1:]:
                create_feed_for_survey_response(database_name, survey_response_id)
        else:
            create_feeds_for_database(database_name)