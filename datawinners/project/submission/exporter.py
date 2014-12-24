from datawinners.project.Header import SubmissionExcelHeader
from datawinners.project.submission.export import export_filename, export_to_new_excel
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.project.submission.submission_search import get_scrolling_submissions_query


class SubmissionExporter:
    def __init__(self, form_model, project_name, dbm, local_time_delta, current_language='en'):
        self.form_model = form_model
        self.project_name = project_name
        self.language = current_language
        self.dbm = dbm
        self.local_time_delta = local_time_delta

    def _get_header_list(self, columns):
        submission_formatter = SubmissionFormatter(columns, self.local_time_delta)
        header_list = submission_formatter.format_header_data()
        return header_list, submission_formatter

    def get_columns_and_search_results(self, query_params, submission_type):
        columns = SubmissionExcelHeader(self.form_model, submission_type, self.language).get_columns()
        search_results, query_fields = get_scrolling_submissions_query(self.dbm, self.form_model, query_params,
                                                                       self.local_time_delta)
        return columns, search_results

    def create_excel_response(self, submission_type, query_params):
        columns, search_results = self.get_columns_and_search_results(query_params, submission_type)
        header_list, submission_formatter = self._get_header_list(columns)
        return export_to_new_excel(header_list, search_results,
                                            export_filename(submission_type, self.project_name), submission_formatter)