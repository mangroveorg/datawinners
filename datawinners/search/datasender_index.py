import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.search.index_utils import _entity_dict, update_ds_mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.documents import FormModelDocument
from mangrove.datastore.entity import get_all_entities
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE, FormModel
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def datasender_search_update(entity_doc, dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_code(dbm, REGISTRATION_FORM_CODE)
        es.index(dbm.database_name, entity_type, _entity_dict(entity_type, entity_doc, dbm, form_model),
                 id=entity_doc.id)
    es.refresh(dbm.database_name)


def update_datasender_mapping(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.form_code == REGISTRATION_FORM_CODE:
        update_ds_mapping(dbm, form_model)


def update_datasender_index(database_name):
    dbm = get_db_manager(database_name)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        update_datasender_mapping(form_model_doc, dbm)
    for entity in get_all_entities(dbm, entity_type=REPORTER_ENTITY_TYPE):
        datasender_search_update(entity, dbm)