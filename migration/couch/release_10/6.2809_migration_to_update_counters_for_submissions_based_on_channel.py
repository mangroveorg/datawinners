import sys
import datetime
from datawinners.accountmanagement.models import OrganizationSetting
from mangrove.transport.contract.survey_response import SMART_PHONE, WEB, SMS, TEST_USER
from datawinners.main.database import get_db_manager

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_start_of_migration

def get_submission_count_aggregate(dbm):
    survey_responses = dbm.load_all_rows_in_view("surveyresponse", reduce=False, include_doc=True)
    year_month_submission_count_dict = {}
    for survey_response in survey_responses:
        if not isinstance(survey_response['value']['submitted_on'], datetime.datetime):
            logging.error("No submitted-on field for survey id:%s, database:%s", survey_response.id, dbm.database_name)
            continue
        year, month = survey_response['value']['submitted_on'].year, survey_response['value']['submitted_on'].month
        key = '%s_%s' % (year, month)
        channel = survey_response['value']['channel']
        if key not in year_month_submission_count_dict:
            year_month_submission_count_dict[key] = {}

        if channel == SMART_PHONE:
            if 'sp_count' in year_month_submission_count_dict[key]:
                year_month_submission_count_dict[key]['sp_count'] += 1
            else:
                year_month_submission_count_dict[key]['sp_count'] = 1
        elif channel == SMS and survey_response['value']['created_by'] == TEST_USER:
            if 'web_count' in year_month_submission_count_dict[key]:
                year_month_submission_count_dict[key]['web_count'] += 1
            else:
                year_month_submission_count_dict[key]['web_count'] = 1
        elif channel != SMS: # should match WEB and EXCEL
            if 'web_count' in year_month_submission_count_dict[key]:
                year_month_submission_count_dict[key]['web_count'] += 1
            else:
                year_month_submission_count_dict[key]['web_count'] = 1

    return year_month_submission_count_dict


def update_counters_for_date(date, key, organization, year_month_submission_count_dict):
    smart_phone_count = year_month_submission_count_dict[key].get('sp_count', 0)
    web_count = year_month_submission_count_dict[key].get('web_count', 0)
    message_tracker = organization._get_message_tracker(date)
    message_tracker.incoming_web_count = web_count
    message_tracker.incoming_sp_count = smart_phone_count
    message_tracker.save()

def update_counters_for_submissions(db_name):
    logger = logging.getLogger(db_name)
    try:
        mark_start_of_migration(db_name)
        logger.info('Starting migration')
        dbm = get_db_manager(db_name)
        year_month_submission_count_dict = get_submission_count_aggregate(dbm)
        organization = OrganizationSetting.objects.get(document_store=dbm.database_name).organization
        for key in year_month_submission_count_dict.keys():
            year, month = int(key.split('_')[0]), int(key.split('_')[1])
            date = datetime.date(year, month, 1)
            update_counters_for_date(date, key, organization, year_month_submission_count_dict)
    except Exception as e:
        logger.exception(e.message)

migrate(all_db_names(), update_counters_for_submissions, version=(10, 0, 6), threads=1)