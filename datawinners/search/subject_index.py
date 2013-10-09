import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import _entity_dict, _mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.documents import FormModelDocument
from mangrove.datastore.entity import get_all_entities
from mangrove.form_model.form_model import FormModel, REGISTRATION_FORM_CODE, get_form_model_by_entity_type


def subject_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == ['reporter']:
        return
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_entity_type(dbm, [entity_type])
        es.index(dbm.database_name, entity_type, _entity_dict(entity_type, entity_doc, dbm, form_model), id=entity_doc.id)
    es.refresh(dbm.database_name)


def _create_mappings(dbm):
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        subject_model_change_handler(form_model_doc, dbm)


def _populate_index(dbm):
    for entity in get_all_entities(dbm):
        subject_search_update(entity, dbm)


def create_subject_index(dbname):
    dbm = get_db_manager(dbname)
    _create_mappings(dbm)
    _populate_index(dbm)


def subject_model_change_handler(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.is_entity_registration_form() and form_model.form_code != REGISTRATION_FORM_CODE:
        _create_subject_mapping(dbm, form_model)


def _create_subject_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    es.put_mapping(dbm.database_name, form_model.entity_type[0], _mapping(form_model.form_code, form_model.fields))

