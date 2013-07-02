import sys
from datawinners.accountmanagement.models import OrganizationSetting, NGOUserProfile
from datawinners.main.database import get_db_manager
from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.survey_response import SurveyResponse

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")

import logging
from migration.couch.utils import init_migrations, should_not_skip, mark_start_of_migration, DWThreadPool, all_db_names

NUMBER_OF_THREADS = 5

init_migrations('/var/log/datawinners/dbs_migrated_release_7_0_1.csv')
logging.basicConfig(filename='/var/log/datawinners/migration_release_7_0_1.log', level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


datasender_by_mobile_include_void="""
function(doc) {
    if (doc.document_type == "Entity" && doc.aggregation_paths._type[0] == 'reporter') {
        var data = doc.data;
        emit(data.mobile_number.value, doc.short_code);
    }
}"""


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


def create_datasender_map(dbm):
    phone_to_rep_id_map = {}
    rep_id_to_uid_map = {}
    for row in dbm.database.query(datasender_by_mobile_include_void):
        phone_to_rep_id_map.update({row.key: row.value})
        rep_id_to_uid_map.update({row.value: row.id})

    return phone_to_rep_id_map, rep_id_to_uid_map


def add_email_info_to_datasender_map(source_to_rep_id_map, org_id):
    profiles = list(NGOUserProfile.objects.filter(org_id=org_id).all())
    for profile in profiles:
        if profile.reporter_id:
            source_to_rep_id_map.update({profile.user.email: profile.reporter_id})
    return  source_to_rep_id_map


def override_owner_with_on_behalf_user(rep_id_to_uid_map, reporter_id, survey_response):
    try:
        rep_id = survey_response.values['eid']
        if rep_id_to_uid_map.get(rep_id):
            return rep_id
    except KeyError as e:
        pass
    return reporter_id


def migrate(db_name):
    try:
        logger = logging.getLogger(db_name)
        logger.info('Starting Migration')
        mark_start_of_migration(db_name)
        dbm = get_db_manager(db_name)

        phone_to_rep_id_map, rep_id_to_uid_map = create_datasender_map(dbm)
        org_id = OrganizationSetting.objects.get(document_store=dbm.database_name).organization_id
        source_to_rep_id_map = add_email_info_to_datasender_map(phone_to_rep_id_map, org_id)

        rows = dbm.database.view("surveyresponse/surveyresponse", reduce=False, include_docs=True)
        for row in rows:
            doc_id = row['value']['_id']
            try:
                original_source = row['value']['source']
            except KeyError as e:
                logger.info("Already migrated %s" % row['value']['_id']) #ignore, document already migrated
                continue

            doc = SurveyResponseDocument.wrap(row['value'])
            survey_response = SurveyResponse.new_from_doc(dbm, doc)

            data_sender_id = source_to_rep_id_map.get(original_source)

            survey_response.created_by = data_sender_id
            survey_response.modified_by = data_sender_id

            owner_short_code = override_owner_with_on_behalf_user(rep_id_to_uid_map, data_sender_id, survey_response)

            owner_uid = rep_id_to_uid_map.get(owner_short_code)
            if owner_uid:
                remove_attr_source_from_survey_response(survey_response)
            else:
                logger.warn("Unable to set owner_uid for source :" + original_source + " doc: " +doc_id)
            survey_response.owner_uid = owner_uid

            survey_response.save()
            logger.info("Migrated %s" % survey_response.id)

        logger.info('Completed Migration')
    except Exception as e:
        logger.exception("FAILED")


def migrate_survey_response_to_add_owner(all_db_names):
    pool = DWThreadPool(NUMBER_OF_THREADS, NUMBER_OF_THREADS)
    for db_name in all_db_names:
        if should_not_skip(db_name):
            pool.submit(migrate, db_name)

    pool.wait_for_completion()
    print "Completed!"

migrate_survey_response_to_add_owner(all_db_names())
# migrate("hni_conservation-south-africa_sgb637896")