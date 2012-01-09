import unittest
from django.forms.fields import CharField, MultipleChoiceField, ChoiceField
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, SelectField
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import Mock
from project.web_questionnaire_form_creator import WebQuestionnaireFormCreater

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
        self.form_model.add_field(self._get_text_field(is_required))

        questionnaire_form_class = WebQuestionnaireFormCreater().create(self.form_model)

        web_text_field = questionnaire_form_class().fields[self.text_field_code]
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(self.instruction,web_text_field.help_text)
        self.assertEqual(is_required,web_text_field.required)


    def test_should_create_web_questionnaire_for_multiple_choice_select_field(self):
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required,False)
        self.form_model.add_field(text_field)

        questionnaire_form_class = WebQuestionnaireFormCreater().create(self.form_model)

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
        questionnaire_form_class = WebQuestionnaireFormCreater().create(self.form_model)

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(ChoiceField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(is_required,web_text_field.required)
        self.assertEqual(expected_choices,web_text_field.choices)

    def test_should_create_hidden_field_for_form_code(self):

        questionnaire_form_class = WebQuestionnaireFormCreater().create(self.form_model)

        web_text_field = questionnaire_form_class().fields['form_code']
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.form_code,web_text_field.initial)

    def test_should_create_web_questionnaire(self):

        self.form_model.add_field(self._get_text_field(False))
        self.form_model.add_field(self._get_select_field(False,False)[1])

        questionnaire_form_class = WebQuestionnaireFormCreater().create(self.form_model)

        web_form = questionnaire_form_class()
        self.assertEqual(3,len(web_form.fields))
        self.assertEqual(CharField,type(web_form.fields[self.form_code]))
        self.assertEqual(CharField,type(web_form.fields[self.text_field_code]))
        self.assertEqual(MultipleChoiceField,type(web_form.fields[self.select_field_code]))


    def _get_select_field(self, is_required,single_select_flag):
        choices = [("Red", "a"), ("Green", "b"), ("Blue", "c")]
        expected_choices = [("a", "Red"), ("b", "Green"), ("c", "Blue")]
        text_field = SelectField(name=self.field_name, code=self.select_field_code, label=self.field_name,
                                 ddtype=Mock(spec=DataDictType),
                                 options=choices, single_select_flag=single_select_flag, required=is_required)
        return expected_choices, text_field

    def _get_text_field(self, is_required):
        text_field = TextField(name=self.field_name, code=self.text_field_code, label=self.field_name,
                               ddtype=Mock(spec=DataDictType),
                               instruction=self.instruction, required=is_required)
        return text_field
