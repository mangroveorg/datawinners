import logging

from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.couchdb.utils import all_db_names
from migration.couch.utils import migrate, mark_as_completed


def update_sms_outgoing_charged_count_for_organization(organization):
    message_trackers = organization._get_all_message_trackers()
    for message_tracker in message_trackers:
        message_tracker.outgoing_sms_charged_count = message_tracker.outgoing_sms_count
        message_tracker.save()


def update_counters_for_submissions(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting migration')
        organization = OrganizationSetting.objects.get(document_store=db_name).organization
        update_sms_outgoing_charged_count_for_organization(organization)
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), update_counters_for_submissions, version=(10, 0, 7), threads=1)