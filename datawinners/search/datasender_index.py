from datawinners.main.database import get_db_manager
from datawinners.project.couch_view_helper import get_all_projects_for_datasender
from datawinners.search.index_utils import _entity_dict, get_fields_mapping, get_elasticsearch_handle
from mangrove.datastore.entity import get_all_entities, _entity_by_short_code
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import get_form_model_by_code, REGISTRATION_FORM_CODE
from mangrove.form_model.project import Project
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def update_datasender_index_by_id(short_code, dbm):
    datasender = _entity_by_short_code(dbm, short_code, REPORTER_ENTITY_TYPE)
    update_datasender_index(datasender, dbm)


def update_datasender_index(entity_doc, dbm):
    es = get_elasticsearch_handle()
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
    return sorted([project.doc['name'] for project in get_all_projects_for_datasender(dbm, entity_id)])


def create_datasender_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    fields = form_model.fields
    fields.append(TextField(name="projects", code='projects', label='projects'))
    es.put_mapping(dbm.database_name, REPORTER_ENTITY_TYPE[0], get_fields_mapping(form_model.form_code, fields))


def update_datasender_for_project_change(project_doc, dbm, old_project=None):
    if not old_project or project_doc.name != old_project.name or project_doc.void != old_project.void:
        project = Project.new_from_doc(dbm, project_doc)
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


def create_ds_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    fields = form_model.fields
    fields.append(TextField(name="projects", code='projects', label='projects'))
    es.put_mapping(dbm.database_name, REPORTER_ENTITY_TYPE[0], get_fields_mapping(form_model.form_code, fields))

