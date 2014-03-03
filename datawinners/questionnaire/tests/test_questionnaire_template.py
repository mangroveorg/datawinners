import json
from unittest import TestCase, SkipTest
from mangrove.datastore.database import _delete_db_and_remove_db_manager
from mangrove.form_model.field import field_to_json
from datawinners.main.database import get_db_manager
from datawinners.questionnaire.library import QuestionnaireLibrary

@SkipTest
class TestQuestionnaireTemplate(TestCase):
    def create_and_test(self):
        dbm = get_db_manager("questionnaire_library")
        _delete_db_and_remove_db_manager(dbm)
        library = QuestionnaireLibrary()
        library.create_template('health_1')
        template = library.get_questionnaire_template('health_1')
        template_details = {'project_name': template.get('name'), 'project_language': template.get('language'),
        'existing_questions':  json.dumps(template.get('json_fields'), default=field_to_json)}
        self.assertEqual(template_details.get('existing_questions'), '')
