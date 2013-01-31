from unittest import TestCase
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import patch, Mock
from datawinners.project.views import get_analysis_response
from project.analysis_result import AnalysisResult

class TestProjectData(TestCase):

    def test_should_return_analysis_response_successfully_for_get_request(self):
        with patch("datawinners.project.views.get_database_manager") as get_database_manager:
            with patch("datawinners.project.views.get_form_model_by_question_code") as get_form_model_by_code:
                with patch("datawinners.project.views.filter_submissions") as filters:
                    with patch("datawinners.project.submission_analyser_helper.get_analysis_result_for_analysis_page") as get_analysis_result:
                        with patch("datawinners.project.header_helper.header_info") as header_info:
                            with patch("datawinners.project.views.project_info") as project_info:
                                request = Mock()
                                request.method = 'GET'
                                get_database_manager.return_value = Mock(spec=DatabaseManager)
                                get_form_model_by_code.return_value = Mock(spec= FormModel)
                                filters.return_value = Mock(spec=list)

                                analysis_result = Mock(spec=AnalysisResult)
                                analysis_result.analysis_result_dict = {"analysis_info" : []}
                                analysis_result.field_values = []
                                get_analysis_result.return_value = analysis_result

                                project_info.return_value = {"project_info" : ''}
                                header_info.return_value =  {"header_info" : []}

                                response = get_analysis_response(request, None, None)

        self.assertTrue({"analysis_info"}.issubset(response.keys()))
        self.assertTrue({"project_info"}.issubset(response.keys()))
        self.assertTrue({"header_info"}.issubset(response.keys()))

