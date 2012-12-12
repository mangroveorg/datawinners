from unittest import TestCase, SkipTest
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import patch, Mock
from datawinners.project.views import get_analysis_response
from project.analysis_result import AnalysisResult

class TestProjectData(TestCase):

    @SkipTest
    def test_should_return_analysis_response_successfully_for_get_request(self):
        expected_analysis_result_keys = ["datasender_list", "default_sort_order", "header_list", "header_type_list", "subject_list",
                   "data_list", "statistics_result"]
        expected_project_info_keys = ["date_format", "is_monthly_reporting", "entity_type", 'project_links', 'project',
                   'questionnaire_code', 'in_trial_mode', 'reporting_period_question_text', 'has_reporting_period',
                   'is_summary_report']

        with patch("datawinners.project.views.get_database_manager") as get_database_manager:
            with patch("datawinners.project.views.get_form_model_by_code") as get_form_model_by_code:
                with patch("datawinners.project.views.build_filters") as build_filters:
                    with patch("datawinners.project.views.project_info") as project_info:
                        with patch("datawinners.project.views.composite_analysis_result") as composite_analysis_result:
                            request = Mock()
                            request.method = 'GET'
                            get_database_manager.return_value = Mock(spec=DatabaseManager)
                            get_form_model_by_code.return_value = Mock(spec=FormModel)
                            build_filters.return_value = Mock(spec=list)
                            analysis_result_mock = Mock(spec=AnalysisResult)
                            analysis_result_mock.field_values = []
                            project_info.return_value = {}.fromkeys(expected_project_info_keys)
                            composite_analysis_result.return_value = {}.fromkeys(expected_analysis_result_keys, [])

                            response = get_analysis_response(request, None, None)

        self.assertTrue(set(expected_analysis_result_keys).issubset(set(response.keys())))
        self.assertTrue(set(expected_project_info_keys).issubset(set(response.keys())))