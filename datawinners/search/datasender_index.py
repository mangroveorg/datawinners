import elasticutils
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.main.database import get_db_manager
from datawinners.project.models import get_all_projects
from datawinners.search.index_utils import _entity_dict, _mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from datawinners.utils import get_organization_from_manager
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


def _is_web_user(dbm, entity_doc):
    organization = get_organization_from_manager(dbm)
    user_profile = NGOUserProfile.objects.filter(reporter_id=entity_doc.short_code, org_id=organization.org_id)
    return bool(user_profile)

def _get_email_by_datasender_id(dbm, short_code):
    organization = get_organization_from_manager(dbm)
    user_profile = NGOUserProfile.objects.filter(reporter_id=short_code, org_id=organization.org_id)
    return user_profile[0].user.email if user_profile else None


def _create_datasender_dict(dbm, entity_doc, entity_type, form_model):
    datasender_dict = _entity_dict(entity_type, entity_doc, dbm, form_model)
    datasender_dict.update({"email": _get_email_by_datasender_id(dbm, entity_doc.short_code)})
    datasender_dict.update({"projects": _get_project_names_by_datasender_id(dbm, entity_doc.short_code)})
    datasender_dict.update({"is_webuser": _is_web_user(dbm, entity_doc)})
    return datasender_dict


def _update_datasender_index(entity_doc, dbm):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    if entity_doc.short_code == 'test':
        return
    if entity_doc.data:
        entity_type = entity_doc.aggregation_paths['_type'][0].lower()
        form_model = get_form_model_by_code(dbm, REGISTRATION_FORM_CODE)
        datasender_dict = _create_datasender_dict(dbm, entity_doc, entity_type, form_model)
        es.index(dbm.database_name, entity_type, datasender_dict, id=entity_doc.id)
    es.refresh(dbm.database_name)


def _create_mappings(dbm):
    for row in dbm.load_all_rows_in_view('questionnaire'):
        form_model_doc = FormModelDocument.wrap(row["value"])
        _create_datasender_mapping(form_model_doc, dbm)


def _populate_index(dbm):
    for entity in get_all_entities(dbm, entity_type=REPORTER_ENTITY_TYPE):
        _update_datasender_index(entity, dbm)


def create_datasender_index(database_name):
    dbm = get_db_manager(database_name)
    _create_mappings(dbm)
    _populate_index(dbm)


def _create_datasender_mapping(form_model_doc, dbm):
    form_model = FormModel.new_from_doc(dbm, form_model_doc)
    if form_model.form_code == REGISTRATION_FORM_CODE:
        _create_ds_mapping(dbm, form_model)


def _create_ds_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    fields = form_model.fields
    fields.append(TextField(name="projects", code='projects', label='projects', ddtype=DataDictType(dbm)))
    fields.append(TextField(name="email", code='email', label='email', ddtype=DataDictType(dbm)))
    es.put_mapping(dbm.database_name, form_model.entity_type[0], _mapping(form_model.form_code, fields))
