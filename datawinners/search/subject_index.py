import elasticutils
from datawinners.search.datasender_index import update_datasender_index
from datawinners.search.index_utils import get_fields_mapping, _entity_dict
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.form_model.form_model import get_form_model_by_entity_type


def create_subject_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    es.put_mapping(dbm.database_name, form_model.entity_type[0], get_fields_mapping(form_model.form_code, form_model.fields))


def entity_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == ['reporter']:
        update_datasender_index(entity_doc, dbm)
        return
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_entity_type(dbm, [entity_type])
        es.index(dbm.database_name, entity_type, _entity_dict(entity_type, entity_doc, dbm, form_model),
                 id=entity_doc.id)
    es.refresh(dbm.database_name)