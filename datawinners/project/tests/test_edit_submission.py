from unittest import TestCase, SkipTest
from django.forms import Form, CharField
from django.http import HttpRequest
from mock import PropertyMock, patch, Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission
from project.edit_submission_view import _map_submission_and_questionnaire, edit_my_submission
from project.models import Project

def question_form_init__(self, *args, **kwargs):
    super(Form, self).__init__(*args, **kwargs)


class TestEdit_submission(TestCase):
    def setUp(self):
        self.manager = PropertyMock(DatabaseManager)
        self.form_model = PropertyMock(return_value=FormModel)


    def test_should_map_submission_values_to_questionnaire(self):
        questionnaire_fields = {'NA': CharField(label='What is your name?')}
        properties = {'fields': questionnaire_fields}
        submission = Submission(self.manager,
            transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'), values={'NA': 'tester'})
        questionnaire_form = type('QuestionnaireForm', (Form, ), properties)
        _map_submission_and_questionnaire(submission, questionnaire_form)
        self.assertEqual('tester', questionnaire_form.fields.get('NA').initial)
        self.assertEqual('What is your name?', questionnaire_form.fields.get('NA').label)

    #TODO:TW_BLR: Fix the mocking for this test(inter modular mocking not working)
    @SkipTest
    def test_should_have_errors_for_invalid_questionnaire(self):
        request = PropertyMock(return_value=HttpRequest)
        submission = Submission(self.manager,
            transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'), values={'na': ''})
        properties = dict()
        properties.update({'NA': CharField(required=True, label='What is your name?')})
        properties.update({'__init__': question_form_init__})
        QuestionnaireForm = type('QuestionnaireForm', (Form,), properties)
        questionnaire_form = QuestionnaireForm(data={'NA': ''})
        with patch('datawinners.project.views._get_form_context') as _get_form_context:
            _get_form_context.return_value = Mock(spec=dict)
            http_response = edit_my_submission(request, submission, questionnaire_form, self.manager,
                PropertyMock(Project),
                self.form_model)

        _get_form_context.assert_called_once()

