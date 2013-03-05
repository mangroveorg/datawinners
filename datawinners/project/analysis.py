from datawinners.project.submission_data import SubmissionData
from datawinners.main.utils import timebox
from datawinners.project.Header import Header
from datawinners.project.analysis_result import AnalysisResult
from datawinners.project.helper import case_insensitive_lookup
from datawinners.project.submission_utils.submission_formatter import SubmissionFormatter
from mangrove.form_model.field import SelectField

# TODO Should rename
class Analysis(SubmissionData):
    def __init__(self, form_model, manager, org_id, filters, keyword=None):
        super(Analysis, self).__init__(form_model, manager, org_id, Header, None, filters, keyword)

    def get_leading_part(self):
        leading_part = []
        for submission in self.filtered_submissions:
            data_sender, rp, subject, submission_date = super(Analysis, self)._get_submission_details(submission)
            leading_part.append(filter(lambda x: x, [submission.id, subject, rp, submission_date, data_sender]))
        return leading_part

    @timebox
    def _get_field_values(self):
        submission_values = [(submission.form_model_revision, submission.values) for submission in
                             self.filtered_submissions]
        field_values = []
        for row in submission_values:
            self._replace_option_with_real_answer_value(row)
            fields_ = [case_insensitive_lookup(field.code, row[-1]) for field in self.form_model.non_rp_fields_by()]
            field_values.append(fields_)

        return field_values

    def _replace_option_with_real_answer_value(self, row):
        assert isinstance(row[-1], dict)
        for question_code, question_value in row[-1].iteritems():
            field = self.form_model.get_field_by_code_and_rev(question_code, row[0])
            if isinstance(field, SelectField):
                row[-1][question_code] = field.get_option_value_list(question_value)

    def analyse(self):
        field_values = SubmissionFormatter().get_formatted_values_for_list(self.get_raw_values())
        analysis_statistics = self.get_analysis_statistics()
        data_sender_list = self.get_data_senders()
        subject_lists = self.get_subjects()
        default_sort_order = self.get_default_sort_order()

        return AnalysisResult(field_values, analysis_statistics, data_sender_list, subject_lists, default_sort_order)