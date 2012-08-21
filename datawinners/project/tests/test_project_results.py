import unittest
from mock import patch, Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import field_attributes, Field
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from project.helper import get_question_answers
from project.views import  get_template_values_for_result_page

class TestProjectResults(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.transport_info = TransportInfo('web', 'source', 'destination')

    def test_should_return_all_project_data(self):
        request = Mock()

        request.method = 'GET'

        questionnaire = Mock()
        question1 = Field(type="", name="q1", code="q1", label='q1', ddtype=DataDictType(self.dbm), instruction='',
            language=field_attributes.DEFAULT_LANGUAGE, constraints=None, required=True)
        questionnaire.fields = [question1]

        submissions = [Submission(self.dbm, self.transport_info, None, values={'q1': 'q1_value'})]
        with patch("project.views._get_submissions") as _get_submissions, patch(
            "project.views._in_trial_mode") as _in_trial_mode:
            _get_submissions.return_value = len(submissions), submissions, None
            _in_trial_mode.return_value = ''
            results = get_template_values_for_result_page(self.dbm, request, None, None, questionnaire, None)
            submissions = results['submissions']
            self.assertEquals(len(submissions), 1)
            self.assertEquals(get_question_answers(submissions[0]), ('q1_value',))

