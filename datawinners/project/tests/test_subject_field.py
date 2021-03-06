import unittest
from django.forms import ChoiceField
from mock import Mock, patch, PropertyMock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import TextField
from datawinners.project.questionnaire_fields import EntityField
from mangrove.form_model.form_model import EntityFormModel


class TestSubjectField(unittest.TestCase):

    def test_create_entity_list_for_subjects(self):
        with patch ("datawinners.project.questionnaire_fields.EntityField._subject_choice_fields") as subject_choice_fields:

            choices = ChoiceField(choices=[('sub1', 'one_subject'), ('sub2', 'another_subject')])
            subject_choice_fields.return_value = choices
            project = EntityFormModel(dbm=Mock(spec=DatabaseManager), entity_type=["some_subject"])

            subject_field = EntityField(Mock(spec=DatabaseManager), project)
            question_field = Mock(spec=TextField)
            question_code = PropertyMock(return_value="eid")
            type(question_field).code = question_code

            result_field = subject_field.create(question_field, 'some_subject')

            self.assertEquals(result_field.get('eid'), choices)
