import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.database import get_db_manager

from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration


def update_sms_outgoing_charged_count_for_organization(organization):
    message_trackers = organization._get_all_message_trackers()
    for message_tracker in message_trackers:
        message_tracker.outgoing_sms_charged_count = message_tracker.outgoing_sms_count
        message_tracker.save()


def update_counters_for_submissions(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        organization = OrganizationSetting.objects.get(document_store=dbm.database_name).organization
        update_sms_outgoing_charged_count_for_organization(organization)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), update_counters_for_submissions, version=(10, 0, 7), threads=1)