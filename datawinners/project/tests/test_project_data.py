from unittest import TestCase
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import patch, Mock
from datawinners.project.views import get_analysis_response
from project.Header import Header
from project.analysis_result import AnalysisResult
from project.tests import form_model_generator

class TestProjectData(TestCase):

    def test_should_return_analysis_response_successfully_for_get_request(self):
        with patch("datawinners.project.views.get_database_manager") as get_database_manager:
            with patch("datawinners.project.views.get_form_model_by_question_code") as get_form_model_by_code:
                with patch("datawinners.project.views.filter_submissions") as filters:
                    with patch("datawinners.project.submission_analyser_helper.get_analysis_result") as get_analysis_result:
                        with patch("datawinners.project.header_helper.header_info") as header_info:
                            with patch("datawinners.project.views.project_info") as project_info:
                                request = Mock()
                                request.method = 'GET'
                                get_database_manager.return_value = Mock(spec=DatabaseManager)
                                get_form_model_by_code.return_value = Mock(spec= FormModel)
                                filters.return_value = Mock(spec=list)

                                analysis_result = Mock(spec=AnalysisResult)
                                analysis_result.analysis_result_dict = {"data_list" : []}
                                analysis_result.field_values = []
                                get_analysis_result.return_value = analysis_result

                                project_info.return_value = {"date_format" : ''}
                                header_info.return_value =  {"header_list" : []}

                                response = get_analysis_response(request, None, None)

        self.assertTrue({"data_list"}.issubset(response.keys()))
        self.assertTrue({"date_format"}.issubset(response.keys()))
        self.assertTrue({"header_list"}.issubset(response.keys()))

    def test_get_analysis_response_is_called(self):
        with patch("datawinners.project.views.get_analysis_response") as get_analysis_response:
            with patch("datawinners.project.views.project_data") as project_data:
                request = Mock()
                project_data(request)
                get_analysis_response.assert_called_with()