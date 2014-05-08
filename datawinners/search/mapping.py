from datawinners.search.datasender_index import create_ds_mapping
from datawinners.search.subject_index import create_subject_mapping
from datawinners.search.submission_index import create_submission_mapping
from mangrove.form_model.form_model import FormModel, REGISTRATION_FORM_CODE, EntityFormModel


def form_model_change_handler(form_model_doc, dbm, old_form_model_doc=None):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    old_form_model = None
    if old_form_model_doc:
        old_form_model = FormModel.new_from_doc(dbm, old_form_model_doc)
    if form_model.form_code != 'delete':
        create_submission_mapping(dbm, form_model, old_form_model)

def entity_form_model_change_handler(entity_form_model_doc,dbm, old_form_model=None):
    entity_form_model = EntityFormModel.new_from_doc(dbm,entity_form_model_doc)
    if entity_form_model.form_code == REGISTRATION_FORM_CODE:
        create_ds_mapping(dbm, entity_form_model)
    else:
        create_subject_mapping(dbm, entity_form_model)
