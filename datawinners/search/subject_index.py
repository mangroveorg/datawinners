import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.search.datasender_index import create_datasender_mapping, update_datasender_index
from datawinners.search.index_utils import _mapping, _entity_dict
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.documents import FormModelDocument
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import FormModel, REGISTRATION_FORM_CODE, get_form_model_by_entity_type
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def _create_mappings(dbm):
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        entity_form_model_change_handler(form_model_doc, dbm)


def _populate_index(dbm):
    rows = dbm.database.iterview('by_short_codes/by_short_codes', 100, reduce=False, include_docs=True)
    for row in rows:
        entity_search_update(Entity.__document_class__.wrap(row.get('doc')), dbm)

def create_entity_index(dbname):
    dbm = get_db_manager(dbname)
    _create_mappings(dbm)
    _populate_index(dbm)


def _create_subject_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    es.put_mapping(dbm.database_name, form_model.entity_type[0], _mapping(form_model.form_code, form_model.fields))


def entity_form_model_change_handler(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.is_entity_registration_form():
        if form_model.form_code == REGISTRATION_FORM_CODE:
            create_datasender_mapping(dbm, form_model)
        else:
            _create_subject_mapping(dbm, form_model)


def entity_search_update(entity_doc, dbm):
    if entity_doc.aggregation_paths['_type'] == REPORTER_ENTITY_TYPE:
        update_datasender_index(entity_doc, dbm)
        return
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_entity_type(dbm, [entity_type])
        es.index(dbm.database_name, entity_type, _entity_dict(entity_type, entity_doc, dbm, form_model),
                 id=entity_doc.id)
    es.refresh(dbm.database_name)