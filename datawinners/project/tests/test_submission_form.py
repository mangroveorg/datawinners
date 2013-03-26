import unittest
from django import forms
from django.forms import CharField, ChoiceField
from mock import Mock, PropertyMock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import IntegerField, DateField, GeoCodeField, TextField
from mangrove.form_model.form_model import FormModel
from project.models import Project
from project.submission_form import SubmissionForm

class TestSubmissionForm(unittest.TestCase):
    def test_should_set_initial_values_for_submissions_with_lower_case_question_codes(self):
        initial_dict = {'q1': 'Ans1', 'q2': 'Ans2'}
        submission_form = SubmissionForm()
        submission_form.fields = {'q1': forms.IntegerField(), 'q2': CharField()}

        submission_form.initial_values(initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('q2').initial)


    def test_should_set_initial_values_for_submissions_with_upper_case_question_codes(self):
        initial_dict = {'Q1': 'Ans1', 'Q2': 'Ans2'}
        submission_form = SubmissionForm()
        submission_form.fields = {'Q1': forms.IntegerField(), 'Q2': CharField()}

        submission_form.initial_values(initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('Q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('Q2').initial)

    def test_should_create_submission_form_with_appropriate_fields(self):
        mock_project = Mock(spec=Project)
        mock_form_model = Mock(spec=FormModel)
        entity_question = PropertyMock(return_value=None)
        fields = [IntegerField('field_name', 'integer_field_code', 'label', Mock),
                  DateField('Date', 'date_field_code', 'date_label', 'dd.mm.yyyy', Mock),
                  GeoCodeField('', 'geo_field_code', '', Mock),
                  TextField('','text_field_code','',Mock)]
        field_property_mock = PropertyMock(return_value=fields)
        type(mock_form_model).fields = field_property_mock
        type(mock_form_model).entity_question = entity_question
        SurveyResponseForm = SubmissionForm.create(Mock(DatabaseManager), mock_project, mock_form_model)
        submission_form_create = SurveyResponseForm()
        expected_field_keys = ['integer_field_code', 'date_field_code','geo_field_code', 'text_field_code','form_code']
        self.assertEquals(submission_form_create.fields.keys(), expected_field_keys)
