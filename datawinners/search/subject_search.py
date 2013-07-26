import elasticutils
from mangrove.datastore.entity import Entity
from datawinners.entity.import_data import get_entity_type_fields, _tabulate_data
from mangrove.form_model.form_model import get_form_model_by_entity_type
from datawinners.settings import ELASTIC_SEARCH_URL


def entity_search_update(entity_doc, dbm):
    if (entity_doc.aggregation_paths['_type'] != ['reporter']):
        subject_search_update(entity_doc, dbm)
    else:
        datasender_search_update(entity_doc, dbm)


def subject_search_update(entity_doc, dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        es.index(dbm.database_name, entity_type, entity_dict(entity_type, entity_doc, dbm), id=entity_doc.id)
    es.refresh(dbm.database_name)


def entity_dict(entity_type, entity_doc, dbm):
    entity = Entity.get(dbm, entity_doc.id)
    fields, labels, codes = get_entity_type_fields(dbm, type=entity_type)
    form_model = get_form_model_by_entity_type(dbm, [entity_type])
    data = _tabulate_data(entity, form_model, codes)
    dictionary = {}
    for index in range(0, len(fields)):
        dictionary.update({fields[index]: data['cols'][index]})
    dictionary.update({"entity_type": entity_type})
    return dictionary


def datasender_search_update(entity, dbm):
    pass

