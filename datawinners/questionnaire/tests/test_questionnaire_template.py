import json
from unittest import TestCase
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import field_to_json
from mock import patch, MagicMock
from datawinners.questionnaire.library import QuestionnaireLibrary


class testQuestionnaireTemplate(TestCase):

    def test_get_category_to_doc_mappings(self):
        with patch('datawinners.questionnaire.library.get_db_manager') as get_db_manager:
            mock_dbm = MagicMock(spec=DatabaseManager)
            get_db_manager.return_value = mock_dbm
            mock_dbm.load_all_rows_in_view.return_value = [
                {'key': 'Health', 'value': {'name': 'one', 'id': 'health1'}},
                {'key': 'Health', 'value': {'name': 'two', 'id': 'health2'}},
                {'key': 'Agriculture', 'value': {'name': 'three', 'id': 'agri1'}}
            ]
            library = QuestionnaireLibrary()

            result = library.get_template_groupings()

            expected = [
                {'category': 'Agriculture', 'templates': [{'id': 'agri1', 'name': 'three'}]},
                {'category': 'Health',
                 'templates': [{'id': 'health1', 'name': 'one'}, {'id': 'health2', 'name': 'two'}]}]
            self.assertDictEqual(expected[0], result[0])
            self.assertDictEqual(expected[1], result[1])

    #Script which creates a template document given project details. Can be used for migrations.
    def create_template_from_project(self):
        #dbm = get_db_manager("questionnaire_library")
        #_delete_db_and_remove_db_manager(dbm)
        library = QuestionnaireLibrary()
        library.create_template_from_project('hni_testorg_slx364903','Health', 'Medicine stock', 'health_2', '026')
        template = library.get_questionnaire_template('health_2')
        template_details = {'project_name': template.get('name'), 'project_language': template.get('language'),
                            'existing_questions': json.dumps(template.get('json_fields'), default=field_to_json)}
        self.assertEqual(template_details.get('project_name'), 'Medicine stock')

