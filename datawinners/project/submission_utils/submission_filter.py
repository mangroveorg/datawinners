import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from datawinners.project.filters import ReportPeriodFilter, SubjectFilter, SurveyResponseDateFilter, DataSenderFilter
from datawinners.questionnaire.helper import get_report_period_question_name_and_datetime_format
from mangrove.transport.contract.survey_response import SurveyResponse
from mangrove.transport.contract.transport_info import TransportInfo

class SurveyResponseFilter(object):

    def __init__(self, params=None, form_model=None):
        self.filter_list = self._build_filters(params, form_model)

    def filter(self, survey_responses):
        if not self.filter_list:
            return survey_responses

        self.to_lowercase_survey_response_keys(survey_responses)

        for filter in self.filter_list:
            survey_responses = filter.filter(survey_responses)

        return survey_responses

    def to_lowercase_survey_response_keys(self, survey_responses):
        for survey_response in survey_responses:
            values = survey_response.values
            survey_response._doc.values = dict((k.lower(), v) for k,v in values.iteritems())

    def _build_filters(self, params, form_model):
        if not params:
            return []
        return filter(lambda x: x is not None,
        [self._build_report_period_filter(form_model, params.get('start_time', ""), params.get('end_time', "")),
         self._build_survey_response_date_filter(params.get('submission_date_start', ""), params.get('submission_date_end', "")),
         self._build_subject_filter(form_model.entity_question.code, params.get('subject_ids', "").strip()),
         self._build_datasender_filter(params.get('submission_sources', "").strip()),
         ])

    def _build_report_period_filter(self, form_model, start_time, end_time):
        if not start_time or not end_time:
            return None
        time_range = {'start': start_time, 'end': end_time}
        question_name, datetime_format = get_report_period_question_name_and_datetime_format(form_model)

        return ReportPeriodFilter(question_name, time_range, datetime_format)

    def _build_survey_response_date_filter(self, start_time, end_time):
        if not start_time or not end_time:
            return None
        time_range = {'start': start_time, 'end': end_time}
        return SurveyResponseDateFilter(time_range)

    def _build_subject_filter(self, entity_question_code, subject_ids):
        if not subject_ids.strip():
            return None
        return SubjectFilter(entity_question_code.lower(), subject_ids)


    def _build_datasender_filter(self, survey_response_sources):
        if not survey_response_sources.strip():
            return None
        return DataSenderFilter(survey_response_sources)


class SurveyResponseFilterTest(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.mock_form_model = Mock(spec=FormModel)
        self.mock_form_model.entity_question.code = '123'

        self.transport_info = TransportInfo('web', 'source', 'destination')
        self.values = [
            {'q1': 'q1', 'q2': '30.07.2012', '123': '001'},
            {'q1': 'q1', 'q2': '30.08.2012', '123': '005'},
            {'q1': 'q1', 'q2': '30.08.2012', '123': '002'},
            ]
        self.survey_responses = [
            SurveyResponse(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[0]),
            SurveyResponse(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[1]),
            SurveyResponse(self.dbm, transport_info=self.transport_info, form_code='test', values=self.values[2])
        ]

    def test_should_return_all_survey_responses_if_filtering_with_no_filters(self):
        filtered_survey_responses = SurveyResponseFilter().filter(survey_responses=self.survey_responses)

        self.assertEqual(3, len(filtered_survey_responses))

    def test_should_return_survey_responses_that_filtered_by_filter_list(self):
        params = {'submission_date_start': '01.01.2013', 'submission_date_end': '30.01.2013', 'subject_ids': '005'}
        filtered_survey_responses = SurveyResponseFilter(params, self.mock_form_model).filter(survey_responses=self.survey_responses)
        self.assertEqual(1, len(filtered_survey_responses))

#    def test_should_return_submissions_that_filtered_by_subject_ids(self):
#            params = {'subject_ids': '006'}
#            filtered_submissions = SubmissionFilter(params, self.mock_form_model).filter(submissions=self.submissions)
#            self.assertEqual(1, len(filtered_submissions))




