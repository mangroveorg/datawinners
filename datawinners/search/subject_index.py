from datawinners.search.datasender_index import update_datasender_index
from datawinners.search.index_utils import _entity_dict, get_elasticsearch_handle
from mangrove.form_model.form_model import get_form_model_by_entity_type
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from datawinners.search.index_utils import get_fields_mapping


def create_subject_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    es.put_mapping(dbm.database_name, form_model.entity_type[0], get_fields_mapping(form_model.form_code, form_model.fields))


def entity_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == REPORTER_ENTITY_TYPE:
        update_datasender_index(entity_doc, dbm)
        return
    es = get_elasticsearch_handle()
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_entity_type(dbm, [entity_type])
        es.index(dbm.database_name, entity_type, _entity_dict(entity_type, entity_doc, dbm, form_model),
                 id=entity_doc.id)
    es.refresh(dbm.database_name)