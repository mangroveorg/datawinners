import logging
from datawinners.main.database import get_db_manager
from datawinners.search import update_submission_search_index, form_model_change_handler, entity_search_update, entity_form_model_change_handler, \
    contact_search_update
from datawinners.search.index_utils import get_elasticsearch_handle
from mangrove.datastore.documents import SurveyResponseDocument, FormModelDocument, EntityFormModelDocument
from mangrove.datastore.entity import Entity, Contact
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
import time
from mangrove.form_model.form_model import FormModel

def populate_submission_index(dbm, form_model_id=None):
    logger = logging.getLogger()
    if form_model_id is None:
        questionnaires = dbm.load_all_rows_in_view("surveyresponse_by_questionnaire_id", reduce=True, group=True)
        for q in questionnaires:
            logger.info('Processing questionnaire id {q}'.format(q=q.key))
            populate_submission_index(dbm, q.key)
    else:
        start = time.time()
        start_key = [form_model_id] if form_model_id else []
        end_key = [form_model_id, {}] if form_model_id else [{}, {}]
        rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000, reduce=False, include_docs=False, startkey=start_key, endkey=end_key)
        form_model = FormModel.get(dbm, form_model_id)
        logger = logging.getLogger(form_model.name)
        ignored = 0
        counter = 0
        error_count = 0
        actions = []
        for row in rows:
            try:
                survey_response = SurveyResponseDocument._wrap_row(row)
                submission_action = update_submission_search_index(survey_response, dbm, refresh_index=False,
                                                                   form_model=form_model, bulk=True)
                actions.append(submission_action)
                counter += 1
                logger.info('No of submissions processed {counter}'.format(counter=counter))
            except FormModelDoesNotExistsException as e:
                ignored += 1
                logger.warning(e.message) # ignore orphaned submissions On changing form code!
            except Exception as ex:
                logger.exception('Exception occurred')
                error_count += 1

        es = get_elasticsearch_handle()
        es.bulk(actions, index=dbm.database_name, doc_type=form_model.id)
                
        logger.warning("No of submissions ignored: {ignored}".format(ignored=ignored))
        logger.warning("No of submissions had errors:{errors}".format(errors=error_count))
            
        logger.info('Time taken (seconds) for indexing {counter} submissions of questionnaire {q} : {timetaken}'
                    .format(counter=counter,q=form_model_id,timetaken=(time.time()-start)))
    


def populate_entity_index(dbm):
    rows = dbm.database.iterview('by_short_codes/by_short_codes', 100, reduce=False, include_docs=True)
    actions = []
    for row in rows:
        try:
            entity = Entity.__document_class__.wrap(row.get('doc'))
            action = entity_search_update(entity, dbm, bulk=True)
            if action is not None: actions.append(action)
        except Exception as e:
            raise e
    es = get_elasticsearch_handle()
    es.bulk(actions)


def populate_contact_index(dbm):
    rows = dbm.database.iterview('datasender_by_mobile/datasender_by_mobile', 100, reduce=False, include_docs=True)
    actions = []
    for row in rows:
        contact = Contact.__document_class__.wrap(row.get('doc'))
        action = contact_search_update(contact, dbm, bulk=True)
        if action is not None: actions.append(action)
    es = get_elasticsearch_handle()
    es.bulk(actions)


def create_all_indices(dbm):
    populate_entity_index(dbm)
    populate_contact_index(dbm)
    populate_submission_index(dbm)


def create_all_mappings(dbm):
    logger = logging.getLogger(dbm.database_name)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        try:
            if row['value']['is_registration_model']:
                entity_form_model_change_handler(EntityFormModelDocument.wrap(row["value"]), dbm)
            else:
                form_model_change_handler(FormModelDocument.wrap(row["value"]), dbm)
        except Exception as e:
            logger.exception(e.message)


if __name__ == '__main__':
    dbm = get_db_manager('hni_testorg_slx364903')
    populate_submission_index(dbm, '54887ad0678e11e5a990080027c7303b')
    #populate_contact_index(dbm)