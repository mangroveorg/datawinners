import cProfile
import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.project.models import get_all_projects, get_all_project_names, get_all_project_names_for_ds
from datawinners.search.index_utils import _entity_dict, _mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import get_all_entities, _entity_by_short_code
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def update_datasender_index_by_id(short_code, dbm):
    datasender = _entity_by_short_code(dbm, short_code, REPORTER_ENTITY_TYPE)
    update_datasender_index(datasender, dbm)


def update_datasender_index(entity_doc, dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.short_code == 'test':
        return
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_code(dbm, REGISTRATION_FORM_CODE)
        datasender_dict = _create_datasender_dict(dbm, entity_doc, entity_type, form_model)
        es.index(dbm.database_name, entity_type, datasender_dict, id=entity_doc.id)
    es.refresh(dbm.database_name)


def _create_datasender_dict(dbm, entity_doc, entity_type, form_model):
    datasender_dict = _entity_dict(entity_type, entity_doc, dbm, form_model)
    datasender_dict.update({"projects": _get_project_names_by_datasender_id(dbm, entity_doc.short_code)})
    return datasender_dict


def _get_project_names_by_datasender_id(dbm, entity_id):
    return sorted([project.value for project in get_all_project_names_for_ds(dbm, entity_id)])


def create_datasender_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    fields = form_model.fields
    fields.append(TextField(name="projects", code='projects', label='projects', ddtype=DataDictType(dbm)))
    es.put_mapping(dbm.database_name, REPORTER_ENTITY_TYPE[0], _mapping(form_model.form_code, fields))


def update_datasender_for_project_change(project, dbm):
    for entity_doc in project.get_associated_datasenders(dbm):
        update_datasender_index(entity_doc, dbm)

def create_datasender_index(database_name):
    dbm = get_db_manager(database_name)
    _create_datasender_mapping(dbm)
    _populate_index(dbm)


def _populate_index(dbm):
    for entity in get_all_entities(dbm, entity_type=REPORTER_ENTITY_TYPE):
        update_datasender_index(entity, dbm)


def _create_datasender_mapping(dbm):
    form_model = get_form_model_by_code(dbm, REGISTRATION_FORM_CODE)
    create_datasender_mapping(dbm, form_model)



