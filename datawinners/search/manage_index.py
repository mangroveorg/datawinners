import logging
from datawinners.main.database import get_db_manager
from datawinners.search import update_submission_search_index, form_model_change_handler, entity_search_update, entity_form_model_change_handler, \
    contact_search_update
from mangrove.datastore.documents import SurveyResponseDocument, FormModelDocument, EntityFormModelDocument
from mangrove.datastore.entity import Entity, Contact
from mangrove.errors.MangroveException import FormModelDoesNotExistsException


def populate_submission_index(dbm, form_model_id=None):
    start_key = [form_model_id] if form_model_id else []
    end_key = [form_model_id, {}] if form_model_id else [{}, {}]
    rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)
    logger = logging.getLogger(dbm.database_name)
    ignored = 0
    for row in rows:
        try:
            survey_response = SurveyResponseDocument._wrap_row(row)
            update_submission_search_index(survey_response, dbm, refresh_index=False)
        except FormModelDoesNotExistsException as e:
            ignored += 1
            logger.warning(e.message) # ignore orphaned submissions On changing form code!
    if ignored > 0:
        logger.warning("Few submissions are ignored %s" % ignored)


def populate_entity_index(dbm):
    rows = dbm.database.iterview('by_short_codes/by_short_codes', 100, reduce=False, include_docs=True)
    for row in rows:
        try:
            entity = Entity.__document_class__.wrap(row.get('doc'))
            entity_search_update(entity, dbm)
        except Exception as e:
            raise e


def populate_contact_index(dbm):
    rows = dbm.database.iterview('datasender_by_mobile/datasender_by_mobile', 100, reduce=False, include_docs=True)
    for row in rows:
        contact = Contact.__document_class__.wrap(row.get('doc'))
        contact_search_update(contact, dbm)


def create_all_indices(dbm):
    populate_entity_index(dbm)
    populate_contact_index(dbm)
    populate_submission_index(dbm)


def create_all_mappings(dbm):
    for row in dbm.load_all_rows_in_view('questionnaire'):
        if row['value']['is_registration_model']:
            entity_form_model_change_handler(EntityFormModelDocument.wrap(row["value"]), dbm)
        else:
            form_model_change_handler(FormModelDocument.wrap(row["value"]), dbm)


if __name__ == '__main__':
    dbm = get_db_manager('hni_testorg_slx364903')
    populate_contact_index(dbm)