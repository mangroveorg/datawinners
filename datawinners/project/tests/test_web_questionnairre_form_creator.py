import unittest
from django.forms.fields import CharField, MultipleChoiceField, ChoiceField
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, SelectField, field_attributes
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import Mock
from mangrove.form_model.validation import TextLengthConstraint
from project.web_questionnaire_form_creator import WebQuestionnaireFormCreater, SubjectQuestionFieldCreator

class TestWebQuestionnaireFormCreator(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.form_code="form_code"
        self.form_model = FormModel(dbm=self.dbm,form_code=self.form_code,name="abc",fields=[])
        self.field_name = "test"
        self.field_code = "code"
        self.instruction = "some instruction"
        self.text_field_code="text"
        self.select_field_code="select"


    def test_should_create_web_questionnaire_for_char_field(self):
        is_required = True
        self.form_model.add_field(self._get_text_field(is_required,False))

        questionnaire_form_class = WebQuestionnaireFormCreater(None).create(self.form_model)

        web_text_field = questionnaire_form_class().fields[self.text_field_code]
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(self.instruction,web_text_field.help_text)
        self.assertEqual(is_required,web_text_field.required)
        self.assertTrue(web_text_field.widget.attrs['watermark'] is not None)
        self.assertEqual('padding-top: 7px;',web_text_field.widget.attrs['style'])


    def test_should_create_web_questionnaire_for_multiple_choice_select_field(self):
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required,False)
        self.form_model.add_field(text_field)

        questionnaire_form_class = WebQuestionnaireFormCreater(None).create(self.form_model)

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(MultipleChoiceField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(is_required,web_text_field.required)
        self.assertEqual(expected_choices,web_text_field.choices)

    def test_should_create_web_questionnaire_for_single_choice_select_field(self):
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required,single_select_flag=True)
        self.form_model.add_field(text_field)
        expected_choices = [('', '--None--'),("a", "Red"), ("b", "Green"), ("c", "Blue")]
        questionnaire_form_class = WebQuestionnaireFormCreater(None).create(self.form_model)

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(ChoiceField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(is_required,web_text_field.required)
        self.assertEqual(expected_choices,web_text_field.choices)

    def test_should_create_hidden_field_for_form_code(self):

        questionnaire_form_class = WebQuestionnaireFormCreater(None).create(self.form_model)

        web_text_field = questionnaire_form_class().fields['form_code']
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.form_code,web_text_field.initial)

    def test_should_create_web_questionnaire(self):

        subject_code = "subject_code"
        self.form_model.add_field(self._get_text_field(True,True, subject_code))
        self.form_model.add_field(self._get_text_field(False,False))
        self.form_model.add_field(self._get_select_field(False,False)[1])
        subject_question_creator_mock = Mock(spec=SubjectQuestionFieldCreator)
        subject_question_creator_mock.create.return_value=ChoiceField()

        questionnaire_form_class = WebQuestionnaireFormCreater(subject_question_creator_mock).create(self.form_model)

        web_form = questionnaire_form_class()
        self.assertEqual(4,len(web_form.fields))

        form_code_hidden_field = web_form.fields[self.form_code]
        self.assertEqual(CharField,type(form_code_hidden_field))

        subject_field = web_form.fields[subject_code]
        self.assertEqual(ChoiceField,type(subject_field))

        simple_text_field = web_form.fields[self.text_field_code]
        self.assertEqual(CharField,type(simple_text_field))

        multiple_choice_field = web_form.fields[self.select_field_code]
        self.assertEqual(MultipleChoiceField,type(multiple_choice_field))

    def _get_mock_project(self):
        project = Mock()
        data_senders = [{field_attributes.NAME: 'reporter1', 'short_name': 'a'},
                {field_attributes.NAME: 'reporter2', 'short_name': 'b'},
        ]
        project.get_data_senders.return_value = data_senders
        return project

    def test_should_pre_populate_datasenders_for_subject_question(self):
        subject_field = self._get_text_field(True,True)
        project = self._get_mock_project()
        display_subject_field = SubjectQuestionFieldCreator(self.dbm,project).create(subject_field)
        self.assertEqual(ChoiceField,type(display_subject_field))
        expected_choices = [('a', 'reporter1'), ('b', 'reporter2')]
        self.assertEqual(expected_choices,display_subject_field.choices)

    def test_should_pre_populate_choices_for_subject_question_on_basis_of_entity_type(self):
        subject_field = self._get_text_field(True,True)
        project = self._get_mock_project()
        project_subject_loader_mock=Mock()
        project_subject_loader_mock.return_value= [{field_attributes.NAME: 'clinic1', 'short_name': 'a'},
                {field_attributes.NAME: 'clinic2', 'short_name': 'b'},
        ]
        project.entity_type.return_value=["Clinic"]
        project.is_on_type.return_value=False
        expected_choices = [('a', 'clinic1'), ('b', 'clinic2')]
        display_subject_field = SubjectQuestionFieldCreator(self.dbm,project,project_subject_loader=project_subject_loader_mock).create(subject_field)
        self.assertEqual(expected_choices,display_subject_field.choices)


    def _get_select_field(self, is_required,single_select_flag):
        choices = [("Red", "a"), ("Green", "b"), ("Blue", "c")]
        expected_choices = [("a", "Red"), ("b", "Green"), ("c", "Blue")]
        text_field = SelectField(name=self.field_name, code=self.select_field_code, label=self.field_name,
                                 ddtype=Mock(spec=DataDictType),
                                 options=choices, single_select_flag=single_select_flag, required=is_required)
        return expected_choices, text_field

    def _get_text_field(self, is_required,entity_question_flag,code=None):
        code=self.text_field_code if code is None else code
        text_field = TextField(name=self.field_name, code=code, label=self.field_name,
                               ddtype=Mock(spec=DataDictType),
                               instruction=self.instruction, required=is_required,constraints=[TextLengthConstraint(1, 20)],entity_question_flag=entity_question_flag)
        return text_field
