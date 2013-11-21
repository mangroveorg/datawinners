from datawinners.main.utils import get_database_name
from datawinners.project.Header import SubmissionExcelHeader
from datawinners.project.submission.export import create_excel_response, export_filename
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.search.submission_search import SubmissionQuery


class SubmissionExporter:
    def __init__(self, form_model, project_name, user):
        self.form_model = form_model
        self.project_name = project_name
        self.db_name = get_database_name(user)
        self.user = user

    def create_excel_response(self, submission_type, criteria):
        columns = SubmissionExcelHeader(self.form_model, submission_type).get_columns()
        query_params = {"search_text": criteria,
                        "start_result_number": 0,
                        "number_of_results": 50000,
                        "order": "",
                        "order_by": 0
        }

        if submission_type != "all":
            query_params.update({"filter": submission_type})
        entity_headers, paginated_query, query_with_criteria = SubmissionQuery(self.form_model,
                                                                               query_params).query_to_be_paginated(
                                                                                self.form_model.id,
                                                                                self.user)
        submission_list = query_with_criteria.values_dict(tuple(entity_headers))

        header_list, formatted_values = SubmissionFormatter(columns).format_tabular_data(submission_list)
        return create_excel_response(header_list, formatted_values, export_filename(submission_type, self.project_name))