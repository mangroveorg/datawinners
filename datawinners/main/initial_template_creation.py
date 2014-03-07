import json
import os
from datawinners.main.database import get_db_manager
from datawinners.questionnaire.library import QuestionnaireTemplateDocument
from mangrove.datastore.database import _delete_db_and_remove_db_manager
import settings


def create_questionnaire_templates():
    dbm = get_db_manager("questionnaire_library")
    _delete_db_and_remove_db_manager(dbm)
    dbm = get_db_manager("questionnaire_library")

    file = settings.PROJECT_DIR+'/questionnaire/template_data.json'
    docs = create_template_from_json_file(file,dbm)
    print docs

def _create_view(dbm):
    from datawinners.main.utils import find_views

    views = find_views('questionnaire_template_view')
    for view_name, view_def in views.iteritems():
        map_function = (view_def['map'] if 'map' in view_def else None)
        reduce_function = (view_def['reduce'] if 'reduce' in view_def else None)
        dbm.create_view(view_name, map_function, reduce_function)

def create_template_from_json_file(dbm, file_name):
    _create_view(dbm)
    docs = []
    with open(file_name) as data_file:
        questionnaires = json.load(data_file)
        for data in questionnaires:
            template_doc = QuestionnaireTemplateDocument(name=data.get('name'), category=data.get('category'))
            template_doc.json_fields = data.get('json_fields')
            template_doc.validators = data.get('validators')
            doc_id = dbm._save_document(template_doc)
            docs.append(doc_id)
    return docs
