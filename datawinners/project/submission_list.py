from datawinners.project.Header import SubmissionsPageHeader
from main.utils import timebox
from project.helper import case_insensitive_lookup
from submission_data import SubmissionData
from mangrove.form_model.field import SelectField

class SubmissionList(SubmissionData):
    def __init__(self, form_model, manager, org_id, submission_type, filters, keyword=None):
        super(SubmissionList, self).__init__(form_model, manager, org_id, SubmissionsPageHeader, submission_type,filters, keyword)

    def get_leading_part(self):
        leading_part = []
        for submission in self.filtered_submissions:
            data_sender, rp, subject, submission_date = super(SubmissionList, self)._get_submission_details(submission)
            status = self._get_translated_submission_status(submission.status)
            error_message = submission.errors if submission.errors else "-"
            leading_part.append(
                filter(lambda x: x, [submission.id, data_sender, submission_date, status, error_message, subject, rp]))
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
