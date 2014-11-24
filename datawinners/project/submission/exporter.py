from datawinners.main.utils import get_database_name
from datawinners.project.Header import SubmissionExcelHeader
from datawinners.project.submission.export import create_excel_response, export_filename
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.search.submission_query import SubmissionQuery, SubmissionQueryResponseCreator, \
    UTCSubmissionQueryResponseCreator


class SubmissionExporter:
    def __init__(self, form_model, project_name, user, current_language='en'):
        self.form_model = form_model
        self.project_name = project_name
        self.db_name = get_database_name(user)
        self.user = user
        self.language = current_language

    def _create_response(self, columns, submission_list, submission_type):
        header_list, formatted_values = SubmissionFormatter(columns).format_tabular_data(submission_list)
        return create_excel_response(header_list, formatted_values, export_filename(submission_type, self.project_name))

    def create_excel_response(self, submission_type, query_params):
        columns = SubmissionExcelHeader(self.form_model, submission_type, self.language).get_columns()

        response_creator = UTCSubmissionQueryResponseCreator(self.form_model)
        entity_headers, paginated_query, query_with_criteria = SubmissionQuery(self.form_model,
                                                                               query_params, response_creator).query_to_be_paginated(
                                                                                self.form_model.id,
                                                                                self.user)
        submission_list = query_with_criteria.values_dict(tuple(entity_headers))

        return self._create_response(columns, submission_list, submission_type)