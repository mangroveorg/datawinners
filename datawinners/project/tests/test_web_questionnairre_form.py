from unittest import TestCase
from django.forms import RegexField, HiddenInput
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import TextField, UniqueIdField
from mangrove.form_model.form_model import FormModel, LOCATION_TYPE_FIELD_NAME
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from datawinners.project.web_questionnaire_form import SubjectRegistrationForm, WebForm, SurveyResponseForm


class TestWebForm(TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_hidden_form_code_field_created(self):
        entity_field = UniqueIdField('clinic',"reporting on", "rep_on", "rep")
        form_model = FormModel(self.dbm, 'some form', 'some', 'form_code_1', fields=[entity_field],
                               entity_type=['Clinic'], type="business")
        form = WebForm(form_model, None)
        self.assertEquals(len(form.fields), 1)
        self.assertEquals(type(form.fields['form_code'].widget), HiddenInput)


class TestSubjectRegistrationForm(TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_regex_field_created_for_entity_question(self):
        entity_field = TextField("reporting on", "rep_on", "rep", entity_question_flag=True)
        form_model = FormModel(self.dbm, 'some form', 'some', 'form_code_1', fields=[entity_field],
                               entity_type=['Clinic'], type="business")

        form = SubjectRegistrationForm(form_model)
        self.assertEquals(type(form.fields['rep_on']), RegexField)
        self.assertEquals(form.short_code_question_code, 'rep_on')

    def test_append_country_to_location(self):
        location_field = TextField(LOCATION_TYPE_FIELD_NAME, "location_code", "some label")
        form_model = FormModel(self.dbm, 'some form', 'some', 'form_code_1', fields=[location_field],
                               entity_type=['Clinic'], type="business")

        form = SubjectRegistrationForm(form_model,
                                       data={'location_code': "Bangalore", 'form_code': 'form_code_1', 't': ['Clinic']},
                                       country='India')
        form.is_valid()
        self.assertEquals(form.cleaned_data['location_code'], 'Bangalore,India')


class TestSurveyResponseForm(TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_should_create_subject_field(self):
        entity_field = TextField("reporting on", "rep_on", "rep", entity_question_flag=True)
        form_model = FormModel(self.dbm, 'some form', 'some', 'form_code_1', fields=[entity_field],
                               entity_type=['Clinic'], type="business")

        subject_field_creator = Mock(spec=SubjectQuestionFieldCreator)
        mock_field = Mock()
        subject_field_creator.create.return_value = mock_field
        form = SurveyResponseForm(form_model, subject_field_creator)

        self.assertEquals(form.fields["rep_on"], mock_field)
        self.assertEquals(type(form.fields['entity_question_code'].widget), HiddenInput)

    def test_should_not_create_subject_fields_if_entity_field_is_not_present_in_form_model(self):
        form_model = FormModel(self.dbm, 'some form', 'some', 'form_code_1', fields=[],
                               entity_type=['Clinic'], type="business")
        form = SurveyResponseForm(form_model, Mock(spec=SubjectQuestionFieldCreator))

        self.assertIsNone(form.fields.get('entity_question_code'))