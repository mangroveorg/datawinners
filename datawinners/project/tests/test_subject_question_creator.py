import unittest
from couchdb.client import Database

from django.forms.fields import ChoiceField
from mock import Mock

from mangrove.form_model.field import TextField, field_attributes, ShortCodeField, UniqueIdField
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.validation import TextLengthConstraint
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator

#Might have duplicate tests have to remove them
class TestSubjectQuestionCreator(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.dbm.database = Mock(spec=Database)
        self.form_code = "form_code"
        self.field_name = "test"
        self.instruction = "some instruction"
        self.subject_data = [
            {'short_code': u'123abc',
             'id': '36998351094511e28aa3406c8f3de0f2',
             'cols': [u'lastlast', u'ff,Madagascar', '18.1324, 27.6547', u'123ABC']
            },
        ]

        self.fields = ['name', 'location', 'geo_code', 'short_code']


    def test_should_pre_populate_choices_for_subject_question_on_basis_of_entity_type(self):
        expected_code = "expected_code"
        subject_field = self._get_unique_id_field(expected_code)
        project = self._get_mock_project()
        option_list = [('clinic1', 'Clinic One  (clinic1)'), ('clinic2', 'Clinic Two  (clinic2)')]
        expected_choices = [('clinic1', 'Clinic One  (clinic1)'), ('clinic2', 'Clinic Two  (clinic2)')]
        subject_question_field_creator = SubjectQuestionFieldCreator(project)
        subject_question_field_creator._get_all_options = Mock(return_value=option_list)
        display_subject_field = subject_question_field_creator.create(subject_field)

        self.assertEqual(expected_choices, display_subject_field.choices)

        subject_question_code_hidden_field_dict = SubjectQuestionFieldCreator(project) \
            .create_code_hidden_field(subject_field)

        self.assertEqual(expected_code, subject_question_code_hidden_field_dict['entity_question_code'].label)

    def _get_unique_id_field(self, code):
        field_name = 'unique_id_field'
        return UniqueIdField(unique_id_type='clinic', name=field_name, code=code, label=field_name,
                               instruction=self.instruction, required=True,
                               constraints=[TextLengthConstraint(1, 20)])


    def _get_mock_project(self):
        project = Mock()
        data_senders = [{field_attributes.NAME: 'reporter1', 'short_code': 'a'},
                        {field_attributes.NAME: 'reporter2', 'short_code': 'b'},
        ]
        project.get_data_senders.return_value = data_senders
        return project


