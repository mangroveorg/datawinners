from datawinners.search import update_submission_search_index, form_model_change_handler, entity_search_update
from mangrove.datastore.documents import SurveyResponseDocument, FormModelDocument
from mangrove.datastore.entity import Entity


def populate_submission_index(dbm):
    rows = dbm.database.iterview("surveyresponse/surveyresponse", 1000,reduce=False,include_docs=False)
    for row in rows:
        survey_response = SurveyResponseDocument._wrap_row(row)
        update_submission_search_index(survey_response, dbm, refresh_index=False)


def populate_entity_index(dbm):
    rows = dbm.database.iterview('by_short_codes/by_short_codes', 100, reduce=False, include_docs=True)
    for row in rows:
        entity = Entity.__document_class__.wrap(row.get('doc'))
        entity_search_update(entity, dbm)

def create_all_indices(dbm):
    populate_entity_index(dbm)
    populate_submission_index(dbm)

def create_all_mappings(dbm):
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        form_model_change_handler(form_model_doc, dbm)

