import json
import os
from datawinners.questionnaire.library import QuestionnaireTemplateDocument
from datawinners.main.database import get_db_manager
from mangrove.datastore.database import _delete_db_and_remove_db_manager
from datawinners import settings


def create_questionnaire_templates():
    db_name = settings.QUESTIONNAIRE_TEMPLATE_DB_NAME
    existing_dbm = get_db_manager(db_name)
    _delete_db_and_remove_db_manager(existing_dbm)
    recreated_dbm = get_db_manager(db_name)

    _create_view(recreated_dbm)

    file = settings.QUESTIONNAIRE_TEMPLATE_JSON_DATA_FILE
    docs = create_template_from_json_file(recreated_dbm, file)
    return docs


def _create_view(dbm):
    from datawinners.main.utils import find_views

    views = find_views('questionnaire_template_view')
    for view_name, view_def in views.iteritems():
        map_function = (view_def['map'] if 'map' in view_def else None)
        reduce_function = (view_def['reduce'] if 'reduce' in view_def else None)
        dbm.create_view(view_name, map_function, reduce_function)


def create_template_from_json_file(dbm, file_name):
    docs = []
    with open(file_name) as data_file:
        questionnaires = json.load(data_file)
        for data in questionnaires:
            template_doc = QuestionnaireTemplateDocument(name=data.get('name'), form_code=data.get('form_code'),
                                                         category=data.get('category'),
                                                         language=data.get('language'))
            template_doc.json_fields = data.get('json_fields')
            template_doc.validators = data.get('validators')
            doc_id = dbm._save_document(template_doc)
            docs.append(doc_id)
    return docs
