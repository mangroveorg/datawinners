from project.submission_analyzer import get_formatted_values_for_list

class AnalysisResult(object):
    def __init__(self, submission_analyzer):
        self.analyzer = submission_analyzer

    def analyze_statistic_results(self):
        raw_field_values = self.analyzer.get_raw_values()
        self._field_values = get_formatted_values_for_list(raw_field_values)
        self._statistics_result = self.analyzer.get_analysis_statistics()

    def analyze_meta_info(self):
        self._header_list, self._header_type_list = self.analyzer.get_headers()
        self._subject_list = self.analyzer.get_subjects()
        self._datasender_list = self.analyzer.get_data_senders()
        self._default_sort_order = self.analyzer.get_default_sort_order()

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