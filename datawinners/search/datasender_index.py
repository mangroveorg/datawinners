import elasticutils
from datawinners.main.database import get_db_manager
from datawinners.project.models import get_all_projects
from datawinners.search.index_utils import _entity_dict, _mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import FormModelDocument
from mangrove.datastore.entity import get_all_entities
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE, FormModel
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def _get_project_names_by_datasender_id(dbm, entity_id):
    project_names = []
    project_list = get_all_projects(dbm, entity_id)
    for project in project_list:
        project_names.append(project.value['name'])
    return project_names


def _create_datasender_dict(dbm, entity_doc, entity_type, form_model):
    datasender_dict = _entity_dict(entity_type, entity_doc, dbm, form_model)
    project_names = _get_project_names_by_datasender_id(dbm, entity_doc.short_code)
    datasender_dict.update({"projects": project_names})
    return datasender_dict


def _datasender_search_update(entity_doc, dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_code(dbm, REGISTRATION_FORM_CODE)
        datasender_dict = _create_datasender_dict(dbm, entity_doc, entity_type, form_model)
        es.index(dbm.database_name, entity_type, datasender_dict, id=entity_doc.id)
    es.refresh(dbm.database_name)

def update_datasender_index(database_name):
    dbm = get_db_manager(database_name)
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        _update_datasender_mapping(form_model_doc, dbm)
    for entity in get_all_entities(dbm, entity_type=REPORTER_ENTITY_TYPE):
        _datasender_search_update(entity, dbm)

def _update_datasender_mapping(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.form_code == REGISTRATION_FORM_CODE:
        _update_ds_mapping(dbm, form_model)

def _update_ds_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    fields = form_model.fields
    fields.append(TextField(name="projects", code='projects', label='projects', ddtype=DataDictType(dbm)))
    es.put_mapping(dbm.database_name, form_model.entity_type[0], _mapping(form_model.form_code, fields))
