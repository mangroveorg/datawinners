from datawinners.project.Header import SubmissionsPageHeader
from datawinners.main.utils import timebox
from datawinners.project.helper import case_insensitive_lookup
from datawinners.project.survey_response_data import SurveyResponseData
from mangrove.form_model.field import SelectField

class SurveyResponseList(SurveyResponseData):
    def __init__(self, form_model, manager, org_id, survey_response_type, filters, keyword=None):
        super(SurveyResponseList, self).__init__(form_model, manager, org_id, SubmissionsPageHeader, survey_response_type,filters, keyword)

    def get_leading_part(self):
        leading_part = []
        for survey_response in self.filtered_survey_responses:
            data_sender, rp, subject, submission_date = super(SurveyResponseList, self)._get_survey_response_details(survey_response)
            status = self._get_translated_survey_response_status(survey_response.status)
            error_message = survey_response.errors if survey_response.errors else "-"
            leading_part.append(
                filter(lambda x: x, [survey_response.id, data_sender, submission_date, status, error_message, subject, rp]))
        return leading_part

    @timebox
    def _get_field_values(self):
        survey_response_values = [(survey_response.form_model_revision, survey_response.values) for survey_response in
                             self.filtered_survey_responses]
        field_values = []
        for row in survey_response_values:
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
