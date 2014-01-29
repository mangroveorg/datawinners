import sys
from mangrove.datastore.documents import FormModelDocument
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import get_elasticsearch_handle
from mangrove.form_model.form_model import get_form_model_by_code, header_fields, FormModel
from mangrove.transport.repository.survey_responses import survey_responses_by_form_code

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
from datawinners.main.couchdb.utils import all_db_names

import logging
from migration.couch.utils import migrate, mark_as_completed

map_form_model_for_projects = """
function(doc) {
   if (doc.document_type == 'FormModel' && doc.is_registration_model == false && !doc.void) {
               emit(doc.form_code, null);
   }
}
"""


def get_deleted_question_codes(form_model, survey_response):
    field_codes = dict((k.lower(), v) for k, v in header_fields(form_model, key_attribute='code').items())
    survey_response_codes = dict((k.lower(), v) for k, v in survey_response.values.items())
    return filter(lambda x: x not in field_codes.keys(), survey_response_codes.keys())


def data_correction(db_name):
    logger = logging.getLogger(db_name)
    try:
        logger.info('Starting indexing')
        dbm = get_db_manager(db_name)
        form_models = dbm.database.query(map_form_model_for_projects, include_docs=True)
        for row in form_models:
            survey_responses = survey_responses_by_form_code(dbm, row.key)
            doc = FormModelDocument.wrap(row.doc)
            form_model = FormModel.new_from_doc(dbm, doc)
            for survey_response in survey_responses:
                deleted_question_codes = get_deleted_question_codes(form_model, survey_response)
                if not deleted_question_codes: continue
                for code in deleted_question_codes:
                    survey_response._doc.values.pop(code, None)
                survey_response.save()
                logger.info('Migrated survey response: ' + survey_response.id + ' deleted fields are: ' + str(
                    deleted_question_codes))
        logger.info('Completed migration')
        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


es = get_elasticsearch_handle()
migrate(all_db_names(), data_correction, version=(10, 0, 1), threads=1)