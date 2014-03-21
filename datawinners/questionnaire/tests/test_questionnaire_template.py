from unittest import TestCase

from mock import patch, MagicMock

from mangrove.datastore.database import DatabaseManager
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

            result = library.get_template_groupings('en')

            expected = [
                {'category': 'Agriculture', 'templates': [{'id': 'agri1', 'name': 'three'}]},
                {'category': 'Health',
                 'templates': [{'id': 'health1', 'name': 'one'}, {'id': 'health2', 'name': 'two'}]}]
            self.assertDictEqual(expected[0], result[0])
            self.assertDictEqual(expected[1], result[1])
            mock_dbm.load_all_rows_in_view.assert_called_with('by_template_category_en')

    def test_template_details_with_french_loaded_when_language_is_french(self):
        with patch('datawinners.questionnaire.library.get_db_manager') as get_db_manager:
            mock_dbm = MagicMock(spec=DatabaseManager)
            get_db_manager.return_value = mock_dbm
            mock_dbm.load_all_rows_in_view.return_value = []
            library = QuestionnaireLibrary()

            library.get_template_groupings('fr')
            mock_dbm.load_all_rows_in_view.assert_called_with('by_template_category_fr')
