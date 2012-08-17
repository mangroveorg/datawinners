import unittest
from mock import patch, Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import field_attributes, Field
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from project.filters import ReportPeriodFilter
from project.helper import get_question_answers
from project.views import  get_template_values_for_result_page

class TestProjectResults(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.transport_info = TransportInfo('web', 'source', 'destination')

    def test_should_return_all_project_data_if_the_project_has_no_report_period_question(self):
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

    def test_should_return_project_data_filtered_by_report_period_if_the_project_has_a_report_period_question(self):
        request = Mock()

        request.method = 'GET'

        questionnaire = Mock()
        question1 = Field(type="", name="q1", code="q1", label='q1', ddtype=DataDictType(self.dbm), instruction='',
            language=field_attributes.DEFAULT_LANGUAGE, constraints=None, required=True)
        questionnaire.fields = [question1]

        submission_within_report_period = Submission(self.dbm, self.transport_info, None, values={'q1': '08.01.2012'})
        submissions = [submission_within_report_period]
        with patch("project.views._get_submissions") as _get_submissions, patch(
            "project.views._in_trial_mode") as _in_trial_mode:
            _get_submissions.return_value = len(submissions), submissions, None
            _in_trial_mode.return_value = ''
            results = get_template_values_for_result_page(self.dbm, request, None, None, questionnaire, None,
                [ReportPeriodFilter('q1', period={'start': '07.31.2012', 'end': '08.30.2012'}, question_format="mm.dd.yyyy")])
            submissions = results['submissions']
            self.assertEquals(len(submissions), 1)
            self.assertEquals(get_question_answers(submissions[0]), ('08.01.2012',))

    def test_should_filter_out_data_not_in_report_period_if_the_project_has_a_report_period_question(self):
        request = Mock()

        request.method = 'GET'

        questionnaire = Mock()
        question1 = Field(type="", name="q1", code="q1", label='q1', ddtype=DataDictType(self.dbm), instruction='',
            language=field_attributes.DEFAULT_LANGUAGE, constraints=None, required=True)
        questionnaire.fields = [question1]

        submission_not_in_report_period = Submission(self.dbm, self.transport_info, None, values={'q1': '01.09.2012'})
        submissions = [submission_not_in_report_period]
        with patch("project.views._get_submissions") as _get_submissions, patch(
            "project.views._in_trial_mode") as _in_trial_mode:
            _get_submissions.return_value = len(submissions), submissions, None
            _in_trial_mode.return_value = ''
            results = get_template_values_for_result_page(self.dbm, request, None, None, questionnaire, None,
                [ReportPeriodFilter('q1', period={'start': '01.08.2012', 'end': '30.08.2012'})])
            submissions = results['submissions']
            self.assertEquals(len(submissions), 0)

    def test_should_raise_exception_when_date_format_does_not_match(self):
        request = Mock()

        request.method = 'GET'

        questionnaire = Mock()
        question1 = Field(type="", name="q1", code="q1", label='q1', ddtype=DataDictType(self.dbm), instruction='',
            language=field_attributes.DEFAULT_LANGUAGE, constraints=None, required=True)
        questionnaire.fields = [question1]

        submission_not_in_report_period = Submission(self.dbm, self.transport_info, None, values={'q1': '2012.09.01'})
        submissions = [submission_not_in_report_period]
        with patch("project.views._get_submissions") as _get_submissions, patch(
            "project.views._in_trial_mode") as _in_trial_mode:
            _get_submissions.return_value = len(submissions), submissions, None
            _in_trial_mode.return_value = ''
            self.assertRaises(ValueError, get_template_values_for_result_page, self.dbm, request, None, None,
                questionnaire, None, [ReportPeriodFilter('q1', period={'start': '01.08.2012', 'end': '30.08.2012'})])

