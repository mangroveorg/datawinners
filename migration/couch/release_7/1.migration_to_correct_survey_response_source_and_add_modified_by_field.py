import sys
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse
from datawinners.project.data_sender_helper import data_sender_by_mobile, data_sender_by_email, get_data_sender_by_reporter_id

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration, all_db_names, DWThreadPool

NUMBER_OF_THREADS = 12

init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_1.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_1.log', level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


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


def migrate(db_name):
    try:
        logger = logging.getLogger(db_name)
        logger.info('Starting Migration')
        mark_start_of_migration(db_name)
        dbm = get_db_manager(db_name)
        rows = dbm.database.iterview("surveyresponse/surveyresponse", 100, reduce=False, include_docs=True)
        try:
            org_id = OrganizationSetting.objects.get(document_store=dbm.database_name).organization_id
        except Exception as e:
            logging.exception("Organization for : %s does not exist.")
            return db_name
        data_sender_dict = dict()
        for row in rows:
            try:
                original_source = row['value']['source']
            except KeyError as e:
                logger.info("Already migrated %s" % row['value']['_id']) #ignore, document already migrated
                continue

            doc = SurveyResponseDocument.wrap(row['value'])
            survey_response = SurveyResponse.new_from_doc(dbm, doc)
            try:
                data_sender = get_data_sender_by_source(dbm, org_id, original_source, survey_response.channel)
            except Exception:
                logger.info("Data sender doesn't exists for survey response: %s" % row['value']['_id'])
                continue
            survey_response.created_by = data_sender[1]
            survey_response.modified_by = data_sender[1]
            try:
                rep_id = survey_response.values['eid']
                if not data_sender_dict.get(rep_id):
                    data_sender_dict.update({rep_id: get_by_short_code_include_voided(dbm, rep_id, ['reporter'])})
                reporter_id = rep_id
            except (DataObjectNotFound, KeyError) as e:
                logger.info("rep info not found for subject(ignored): %s " % (survey_response.uuid))
                reporter_id = data_sender[1]
            owner_uid = None
            try:
                owner_uid = get_data_sender_by_reporter_id(dbm, reporter_id).id
                remove_attr_source_from_survey_response(survey_response)
            except Exception as e:
                logging.exception("Unable to set owner_uid " + e.message)
            survey_response.owner_uid = owner_uid

            survey_response.save()
            logger.info("Migrated %s" % survey_response.id)

        logger.info('Completed Migration')
    except Exception as e:
        logging.exception("FAILED")


def get_data_sender_by_source(dbm, org_id, original_source, channel):
    if channel == 'sms':
        return tuple(data_sender_by_mobile(dbm, original_source) + [original_source])
    else:
        return data_sender_by_email(org_id, original_source)


def migrate_survey_response_to_add_owner(all_db_names):
    pool = DWThreadPool(NUMBER_OF_THREADS, NUMBER_OF_THREADS)
    for db_name in all_db_names:
        if should_not_skip(db_name):
            pool.submit(migrate, db_name)

    pool.wait_for_completion()
    print "Completed!"


migrate_survey_response_to_add_owner(all_db_names())
