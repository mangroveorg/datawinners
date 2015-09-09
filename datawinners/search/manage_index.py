import logging
from datawinners.main.database import get_db_manager
from datawinners.search import update_submission_search_index, form_model_change_handler, entity_search_update, entity_form_model_change_handler, \
    contact_search_update
from mangrove.datastore.documents import SurveyResponseDocument, FormModelDocument, EntityFormModelDocument
from mangrove.datastore.entity import Entity, Contact
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
import time
from mangrove.form_model.form_model import FormModel

def populate_submission_index(dbm, form_model_id=None):
    logger = logging.getLogger()
    if form_model_id is None:
        questionnaires = dbm.database.iterview("surveyresponse_by_questionnaire_id/surveyresponse_by_questionnaire_id", 1, reduce=True, group=True)
        for q in questionnaires:
            logger.info('Processing questionnaire id {q}'.format(q=q.key))
            populate_submission_index(dbm, q.key)
        
    start = time.time()
    start_key = [form_model_id] if form_model_id else []
    end_key = [form_model_id, {}] if form_model_id else [{}, {}]
    rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)
    form_model = FormModel.get(dbm, form_model_id)
    ignored = 0
    counter = 0
    for row in rows:
        try:
            survey_response = SurveyResponseDocument._wrap_row(row)
            update_submission_search_index(survey_response, dbm, refresh_index=False, form_model=form_model)
            counter += 1
            logger.info('No of submissions processed {counter}'.format(counter=counter))
        except FormModelDoesNotExistsException as e:
            ignored += 1
            logger.warning(e.message) # ignore orphaned submissions On changing form code!
        except Exception as ex:
            logger.exception('Exception occurred')
    if ignored > 0:
        logger.warning("Few submissions are ignored %s" % ignored)
    logger.info('Time taken (seconds) for indexing {counter} submissions of questionnaire {q} : {timetaken}'
                .format(counter=counter,q=form_model_id,timetaken=(time.time()-start)))
    


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