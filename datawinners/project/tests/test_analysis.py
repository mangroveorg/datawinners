# import unittest
# from mock import patch, PropertyMock
# from mangrove.datastore.database import DatabaseManager
# from mangrove.form_model.form_model import FormModel
# from mangrove.transport.contract.submission import Submission
# from project.analysis import Analysis
# from mangrove.transport import TransportInfo
#
# class TestAnalysis(unittest.TestCase):
#     def setUp(self):
#         self.form_model = PropertyMock(return_value=FormModel)
#         self.manager = PropertyMock(return_value=DatabaseManager)
#         self.filters = {u"name": "abcd"}
#
#     def test_should_return_leading_part_of_submissions(self):
#         with patch("datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
#             with patch(
#                 "datawinners.project.survey_response_data.SurveyResponseData._get_survey_response_details") as get_submission_details:
#                 submission = Submission(self.manager, form_code="cli001",
#                     transport_info=TransportInfo(transport='SMS', source='123', destination='456'),
#                     values={"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
#                 get_submissions.return_value = [submission]
#                 get_submission_details.return_value = (
#                                                       'Tester Pune', 'admin', 'tester150411@gmail.com'), "12-03-2012", (
#                                                           'Clinic-One', u'cli15'), "23-02-2012"
#                 analysis_data = Analysis(self.form_model, self.manager, "org_id", self.filters)
#                 leading_part = analysis_data.get_raw_values()
#                 expected_leading_part = [
#                     [submission.id, ('Clinic-One', u'cli15'), "12-03-2012", "23-02-2012", ('Tester Pune', 'admin', 'tester150411@gmail.com')]]
#                 self.assertEqual(expected_leading_part, leading_part)
