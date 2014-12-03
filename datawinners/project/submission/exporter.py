import logging
import resource
from datawinners.project.Header import SubmissionExcelHeader
from datawinners.project.submission.export import export_filename, create_zipped_excel_response
from datawinners.project.submission.formatter import SubmissionFormatter
from datawinners.project.submission.submission_search import get_scrolling_submissions_query

logger = logging.getLogger("datawinners")


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

        logger.error('Memory usage after tabulation: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

        return create_zipped_excel_response(header_list, formatted_values,
                                            export_filename(submission_type, self.project_name))

    def create_excel_response(self, submission_type, query_params):
        columns = SubmissionExcelHeader(self.form_model, submission_type, self.language).get_columns()

        logger.error("Before es query")
        logger.error('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        memory_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        search_results, query_fields = get_scrolling_submissions_query(self.dbm, self.form_model, query_params,
                                                                       self.local_time_delta)
        memory_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.error("Change in memeory: %s (kb)" % (memory_after-memory_before))
        logger.error('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

        return self._create_response(columns, search_results, submission_type)