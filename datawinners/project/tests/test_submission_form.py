import unittest
from django.forms import ChoiceField
from mock import Mock, PropertyMock, patch, MagicMock
from datawinners.project.models import Project
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import IntegerField, DateField, GeoCodeField, TextField, UniqueIdField
from datawinners.project.submission_form import EditSubmissionForm


class TestSubmissionForm(unittest.TestCase):
    def setUp(self):
        self.manager = Mock(spec=DatabaseManager)
        self.project = Mock(spec=Project, get_data_senders=Mock(return_value=[{'short_code':'ds1', 'name':'DS Name'}]))

    def test_should_set_initial_values_for_submissions_with_lower_case_question_codes(self):
        initial_dict = {'q1': 'Ans1', 'q2': 'Ans2'}
        type(self.project).fields = PropertyMock(
            return_value=[TextField(name="q1", code="q1", label="some"),
                          TextField(name="q2", code="q2", label="some")])
        submission_form = EditSubmissionForm(self.manager, self.project, initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('q2').initial)


    def test_should_set_initial_values_for_submissions_with_upper_case_question_codes(self):
        initial_dict = {'Q1': 'Ans1', 'Q2': 'Ans2'}
        type(self.project).fields = PropertyMock(
            return_value=[TextField(name="Q1", code="Q1", label="some" ),
                          TextField(name="Q2", code="Q2", label="some" )])
        submission_form = EditSubmissionForm(self.manager, self.project, initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('Q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('Q2').initial)

    def test_should_create_submission_form_with_appropriate_fields(self):
        fields = [IntegerField('field_name', 'integer_field_code', 'label', Mock),
                  DateField('Date', 'date_field_code', 'date_label', 'dd.mm.yyyy', Mock),
                  GeoCodeField('', 'geo_field_code', '', Mock),
                  TextField('', 'text_field_code', '')]
        type(self.project).fields = PropertyMock(return_value=fields)

        submission_form_create = EditSubmissionForm(self.manager, self.project, {})
        expected_field_keys = ['form_code', 'dsid', 'integer_field_code', 'date_field_code', 'geo_field_code',
                               'text_field_code']
        self.assertListEqual(submission_form_create.fields.keys(), expected_field_keys)

    def test_entity_question_form_field_created(self):
        project = MagicMock(spec=Project)
        fields = [
            UniqueIdField("clinic","entity question", "q1", "what are you reporting on?")]
        project.form_code = '001'
        project.fields = fields

        with patch.object(SubjectQuestionFieldCreator, 'create') as create_entity_field:
            choice_field = ChoiceField(('sub1', 'sub2', 'sub3'))
            create_entity_field.return_value = choice_field
            submission_form = EditSubmissionForm(self.manager, project,  {})
            self.assertEqual(choice_field, submission_form.fields['q1'])
