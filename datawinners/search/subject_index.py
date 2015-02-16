from datawinners.search.datasender_index import update_datasender_index
from datawinners.search.index_utils import get_elasticsearch_handle, get_field_definition, get_fields_mapping_by_field_def, \
    subject_dict, \
    es_questionnaire_field_name
from mangrove.form_model.form_model import get_form_model_by_entity_type
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def create_subject_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    fields_definition = []
    for field in form_model.fields:
        fields_definition.append(
            get_field_definition(field, field_name=es_questionnaire_field_name(field.code, form_model.id)))
    mapping = get_fields_mapping_by_field_def(doc_type=form_model.id, fields_definition=fields_definition)
    es.put_mapping(dbm.database_name, form_model.entity_type[0], mapping)


def entity_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == REPORTER_ENTITY_TYPE:
        update_datasender_index(entity_doc, dbm)
        return
    es = get_elasticsearch_handle()
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_entity_type(dbm, [entity_type])
        es.index(dbm.database_name, entity_type, subject_dict(entity_type, entity_doc, dbm, form_model),
                 id=entity_doc.id)
    es.refresh(dbm.database_name)


def contact_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == REPORTER_ENTITY_TYPE:
        update_datasender_index(entity_doc, dbm)
        return