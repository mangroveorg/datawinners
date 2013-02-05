from unittest import TestCase
from django.forms import Form, CharField
from mock import PropertyMock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission
from project.edit_submission_view import _map_submission_and_questionnaire


class TestEdit_submission(TestCase):
    def setUp(self):
        self.manager = PropertyMock(return_value=DatabaseManager)
        self.form_model = PropertyMock(return_value=FormModel)

        
    def test_should_map_submission_values_to_questionnaire(self):
        questionnaire_fields = {'NA': CharField(label='What is your name?')}
        properties= {'fields': questionnaire_fields}
        submission = Submission(self.manager,transport_info=TransportInfo('web','tester150411@gmail.com','destination'),values={'na':'tester'})
        questionnaire_form = type('QuestionnaireForm', (Form, ), properties)
        _map_submission_and_questionnaire(submission,questionnaire_form)
        self.assertEqual('tester',questionnaire_form.fields.get('NA').initial)
        self.assertEqual('What is your name?',questionnaire_form.fields.get('NA').label)