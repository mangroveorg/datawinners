from collections import OrderedDict

from datawinners.project.Header import SubmissionExcelHeader
from datawinners.project.preferences import get_zero_indexed_columns_to_hide
from datawinners.project.submission.export import export_filename, export_to_new_excel
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.project.submission.submission_search import SubmissionSearch


class SubmissionExporter:
    def __init__(self, form_model, project_name, dbm, local_time_delta, user, current_language='en', only_visible=False):
        self.user = user
        self.only_visible = only_visible
        self.form_model = form_model
        self.project_name = project_name
        self.language = current_language
        self.dbm = dbm
        self.local_time_delta = local_time_delta

    def _get_header_list(self, columns):
        submission_formatter = \
            SubmissionFormatter(columns, self.local_time_delta)
        header_list = submission_formatter.format_header_data()
        return header_list, submission_formatter

    # def _create_zipped_response(self, columns, submission_list, submission_type):
    #     header_list, submission_formatter = self._get_header_list(columns)
    #     return export_to_zipped_excel(header_list, submission_list,
    #                                         export_filename(submission_type, self.project_name), submission_formatter)

    # def _create_excel_response(self, columns, submission_list, submission_type):
    #     header_list, submission_formatter = self._get_header_list(columns)
    #     return export_to_excel_no_zip(header_list, submission_list,
    #                                   export_filename(submission_type, self.project_name), submission_formatter)

    def _get_skip_fields(self, submission_type):
        if self.only_visible:
            return get_zero_indexed_columns_to_hide(self.user, submission_type, self.form_model.id)
        return []

    def get_columns_and_search_results(self, query_params, submission_type):
        columns = SubmissionExcelHeader(self.dbm, self.form_model, submission_type, self.language).get_columns()
        skip_fields = self._get_skip_fields(submission_type)
        submission_search = SubmissionSearch(self.dbm, self.form_model, query_params, self.local_time_delta, skip_fields)
        search_results, query_fields = submission_search.get_scrolling_submissions_query()
        return columns, search_results

    def get_export_data(self, query_params, submission_type):
        columns, search_results = self.get_columns_and_search_results(query_params, submission_type)
        skip_fields = self._get_skip_fields(submission_type)
        columns = OrderedDict([(j, columns[j]) for i, j in enumerate(columns) if i not in skip_fields])
        return columns, search_results

    def create_excel_response(self, submission_type, query_params):
        columns, search_results = self.get_export_data(query_params, submission_type)
        return self._create_response(columns, search_results, submission_type)

    def _create_response(self, columns, submission_list, submission_type):
        header_list, submission_formatter = self._get_header_list(columns)
        return export_to_new_excel(header_list, submission_list, export_filename(submission_type, self.project_name),
                                   submission_formatter)
