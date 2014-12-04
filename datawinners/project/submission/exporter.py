from datawinners.project.Header import SubmissionExcelHeader
from datawinners.project.submission.export import export_filename, create_zipped_excel_response
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.project.submission.submission_search import get_scrolling_submissions_query


class SubmissionExporter:
    def __init__(self, form_model, project_name, dbm, local_time_delta, current_language='en'):
        self.form_model = form_model
        self.project_name = project_name
        self.language = current_language
        self.dbm = dbm
        self.local_time_delta = local_time_delta

    def _create_response(self, columns, submission_list, submission_type):
        header_list, formatted_values = SubmissionFormatter(columns, self.local_time_delta).format_tabular_data(
            submission_list)
        return create_zipped_excel_response(header_list, formatted_values,
                                            export_filename(submission_type, self.project_name))

    def create_excel_response(self, submission_type, query_params):
        columns = SubmissionExcelHeader(self.form_model, submission_type, self.language).get_columns()

        search_results, query_fields = get_scrolling_submissions_query(self.dbm, self.form_model, query_params,
                                                                       self.local_time_delta)

        return self._create_response(columns, search_results, submission_type)