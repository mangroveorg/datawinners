import unittest

from django.forms.fields import ChoiceField
from mock import Mock

from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, field_attributes
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import TextLengthConstraint
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator

#Might have duplicate tests have to remove them
class TestSubjectQuestionCreator(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.form_code = "form_code"
        self._get_form_model()
        self.field_name = "test"
        self.short_code_question_code = "short_code_question_field_name"
        self.instruction = "some instruction"
        self.text_field_code = "text"
        self.subject_data = [
            {'short_code': u'123abc',
             'id': '36998351094511e28aa3406c8f3de0f2',
             'cols': [u'lastlast', u'ff,Madagascar', '18.1324, 27.6547', u'123ABC']
            },
        ]

        self.fields = ['name', 'location', 'geo_code', 'short_code']


    def test_should_pre_populate_datasenders_for_subject_question(self):
        subject_field = self._get_text_field(True, True)
        project = self._get_mock_project()
        display_subject_field = SubjectQuestionFieldCreator(self.dbm, project).create(subject_field)
        self.assertEqual(ChoiceField, type(display_subject_field))
        expected_choices = [('a', 'reporter1  (a)'), ('b', 'reporter2  (b)')]
        self.assertEqual(expected_choices, display_subject_field.choices)

    def test_should_pre_populate_choices_for_subject_question_on_basis_of_entity_type(self):
        expected_code = "expected_code"
        subject_field = self._get_text_field(True, True, expected_code)
        project = self._get_mock_project()
        project_subject_loader_mock = Mock()
        fields = ['name', 'short_code']
        label = None
        project_subject_loader_mock.return_value = [{'short_code': 'a', 'cols': ['clinic1', 'a']},
                                                    {'short_code': 'b', 'cols': ['clinic2', 'b']},
                                                   ], fields, label
        project.entity_type.return_value = ["Clinic"]
        project.is_on_type.return_value = False
        expected_choices = [('a', 'clinic1  (a)'), ('b', 'clinic2  (b)')]
        display_subject_field = SubjectQuestionFieldCreator(self.dbm, project,
                                                            project_subject_loader=project_subject_loader_mock).create(
            subject_field)

        self.assertEqual(expected_choices, display_subject_field.choices)

        subject_question_code_hidden_field_dict = SubjectQuestionFieldCreator(self.dbm, project,
                                                                              project_subject_loader=project_subject_loader_mock) \
            .create_code_hidden_field(subject_field)

        self.assertEqual(expected_code, subject_question_code_hidden_field_dict['entity_question_code'].label)

    def _get_text_field(self, is_required, entity_question_flag, code=None):
        code = self.text_field_code if code is None else code
        field_name = self.field_name if not entity_question_flag else self.short_code_question_code
        text_field = TextField(name=field_name, code=code, label=field_name,
                               ddtype=Mock(spec=DataDictType),
                               instruction=self.instruction, required=is_required,
                               constraints=[TextLengthConstraint(1, 20)],
                               entity_question_flag=entity_question_flag)
        return text_field


    def _get_mock_project(self):
        project = Mock()
        data_senders = [{field_attributes.NAME: 'reporter1', 'short_code': 'a'},
                        {field_attributes.NAME: 'reporter2', 'short_code': 'b'},
        ]
        project.get_data_senders.return_value = data_senders
        return project


    def _get_form_model(self, is_registration_form=False):
        return FormModel(dbm=self.dbm, form_code=self.form_code, name="abc", fields=[],
                         is_registration_model=is_registration_form, entity_type=["entity_type"])


    def test_build_subject_choice_data(self):
        creator = SubjectQuestionFieldCreator(None, None)

        data = creator._build_subject_choice_data(self.subject_data, self.fields)[0]
        self.assertEqual(u'123abc', data['unique_id'])
        self.assertEqual(u'lastlast', data['name'])

    def test_should_build_choice_from_subject(self):
        creator = SubjectQuestionFieldCreator(None, None)

        data = {'name': 'lastlast', 'location': u'ff,Madagascar', 'geo_code': '18.1324, 27.6547',
                'short_code': u'123ABC', 'unique_id': '123abc'}

        choice = creator._data_to_choice(data)

        self.assertEqual((u'123abc', u'lastlast  (123ABC)'), choice)