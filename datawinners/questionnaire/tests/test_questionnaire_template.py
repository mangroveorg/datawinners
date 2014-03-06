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
                {'key': 'Health', 'value': [
                    ['one', 'health1'],
                    ['two','health2']
                ]},

                {'key': 'Agriculture', 'value': [['three', 'agri1']]}
            ]
            library = QuestionnaireLibrary()

            result = library.get_template_groupings()

            expected = [
                {'category': 'Health',
                 'templates': [{'name': 'one','id': 'health1'}, {'name': 'two','id': 'health2',}]},
                {'category': 'Agriculture', 'templates': [{'name': 'three', 'id': 'agri1'}]},]
            self.assertListEqual(expected, result)

