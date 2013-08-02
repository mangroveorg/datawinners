from datawinners.search.subject_search import update_search, update_mapping
from mangrove.form_model.form_model import FormModel, REGISTRATION_FORM_CODE


def entity_search_update(entity_doc, dbm):
    if (entity_doc.aggregation_paths['_type'] != ['reporter']):
        update_search(entity_doc, dbm)
    else:
        datasender_search_update(entity_doc, dbm)


def update_index(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.is_entity_registration_form() and form_model.form_code != REGISTRATION_FORM_CODE:
        update_mapping(dbm, form_model)


def datasender_search_update(entity, dbm):
    pass
