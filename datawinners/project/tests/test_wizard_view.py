import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from datawinners.project.wizard_view import _get_deleted_question_codes


class TestWizardView(unittest.TestCase):
    def test_should_give_deleted_question_codes(self):
        old_form_model = Mock()
        old_form_model.field_codes.return_value = ['q1', 'q2', 'q3']
        new_form_model = Mock()
        new_form_model.field_codes.return_value = ['q4', 'q5', 'q3']
        result = _get_deleted_question_codes(old_form_model=old_form_model, new_form_model=new_form_model)
        self.assertEqual(result, ['q1', 'q2'])