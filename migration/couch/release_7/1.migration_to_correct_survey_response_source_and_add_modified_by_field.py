import sys
from datawinners import settings
from datawinners.accountmanagement.models import OrganizationSetting
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse
from datawinners.project.data_sender_helper import data_sender_by_mobile, data_sender_by_email, get_data_sender_by_reporter_id

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration, all_db_names
from mangrove.datastore.database import get_db_manager

init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_2.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_2.log', level=logging.DEBUG,
                    format="%(asctime)s;%(levelname)s;%(message)s")


def _get_form_model(dbm, form_model_dict, survey_response):
    if not form_model_dict.get(survey_response.form_code):
        form_model_dict.update({survey_response.form_code: get_form_model_by_code(dbm, survey_response.form_code)})
    form_model = form_model_dict.get(survey_response.form_code)
    return form_model


def remove_attr_source_from_survey_response(survey_response):
    try:
        survey_response._doc._data.pop('source')
    except KeyError:
        pass


def migrate(database_name):
    logging.info('Starting Migration for: %s' % database_name)
    dbm = get_db_manager(server=settings.COUCH_DB_SERVER, database=database_name)
    rows = dbm.view.surveyresponse(reduce=False, include_docs=True)
    try:
        org_id = OrganizationSetting.objects.get(document_store=dbm.database_name).organization_id
    except Exception as e:
        logging.exception("Organization for : %s does not exist." % database_name)
        return database_name
    data_sender_dict = dict()
    if len(rows):
        for row in rows:
            try:
                original_source = row['doc']['source']
            except KeyError as e:
                #logging.info("Already migrated %s" % row['doc']['_id']) #ignore, document already migrated
                continue

            doc = SurveyResponseDocument.wrap(row['doc'])
            survey_response = SurveyResponse.new_from_doc(dbm, doc)
            remove_attr_source_from_survey_response(survey_response)
            try:
                data_sender = get_data_sender_by_source(dbm, org_id, original_source, survey_response.channel)
            except Exception:
                logging.info("Data sender doesn't exists for survey response: %s" % row['doc']['_id'])
                continue
            survey_response.created_by = data_sender[1]
            survey_response.modified_by = data_sender[1]
            try:
                rep_id = survey_response.values['eid']
                if not data_sender_dict.get(rep_id):
                    data_sender_dict.update({rep_id: get_by_short_code_include_voided(dbm, rep_id, ['reporter'])})
                reporter_id = rep_id
            except (DataObjectNotFound, KeyError) as e:
                logging.info("rep info not found for subject(ignored): %s " % (survey_response.uuid))
                reporter_id = data_sender[1]
            try:
                survey_response.owner_uid = get_data_sender_by_reporter_id(dbm, reporter_id).id
            except Exception as e:
                pass

            survey_response.save()


    logging.info('Completed Migration: %s' % database_name)


def get_data_sender_by_source(dbm, org_id, original_source, channel):
    if channel == 'sms':
        return tuple(data_sender_by_mobile(dbm, original_source) + [original_source])
    else:
        return data_sender_by_email(org_id, original_source)


def migrate_survey_response_to_add_owner(all_db_names):
    for database in all_db_names:
        try:
            if should_not_skip(database):
                mark_start_of_migration(database)
                migrate(database)
        except Exception as e:
            logging.exception("Failed Database: %s Error %s" % (database, e.message))


migrate_survey_response_to_add_owner(all_db_names())
