from main.utils import timebox
from mangrove.utils.json_codecs import encode_json
from project.Header import Header
from project.submission_utils.submission_formatter import SubmissionFormatter


class AnalysisResult(object):
    def __init__(self, submission_analyzer, header_class=Header, with_status=False):
        self.analyzer = submission_analyzer
        self.header_class = header_class
        self.with_status = with_status

        self._analyze_statistic_results()

    @timebox
    def _analyze_statistic_results(self):
        self._field_values = SubmissionFormatter().get_formatted_values_for_list(self.analyzer.get_raw_values())
        self._statistics_result = self.analyzer.get_analysis_statistics()

    @timebox
    def _analyze_meta_info(self):
        self._header_list, self._header_type_list = self.header_class(self.analyzer.form_model).get()
        self._subject_list = self.analyzer.get_subjects()
        self._datasender_list = self.analyzer.get_data_senders()
        self._default_sort_order = self.analyzer.get_default_sort_order()

    def analysis_result_dict(self):
        self._analyze_meta_info()

        return {"datasender_list": self.datasender_list,
                "default_sort_order": repr(encode_json(self.default_sort_order)),
                "header_list": self.header_list,
                "header_name_list": repr(encode_json(self.header_list)),
                "header_type_list": repr(encode_json(self.header_type_list)),
                "subject_list": self.subject_list,
                "data_list": repr(encode_json(self.field_values)),
                "statistics_result": repr(encode_json(self.statistics_result))}


    @property
    def statistics_result(self):
        return self._statistics_result

    @property
    def field_values(self):
        return self._field_values

    @property
    def header_list(self):
        return self._header_list

    @property
    def header_type_list(self):
        return self._header_type_list

    @property
    def subject_list(self):
        return self._subject_list

    @property
    def datasender_list(self):
        return self._datasender_list

    @property
    def default_sort_order(self):
        return self._default_sort_order