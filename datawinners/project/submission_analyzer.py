from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import DataObjectNotFound
import re
from mangrove.form_model.field import SelectField
from mangrove.form_model.form_model import FormModel
from project import helper
from project.helper import filter_submissions, get_data_sender, _to_str, case_insensitive_lookup, NOT_AVAILABLE
from enhancer import form_model_enhancer, field_enhancer

NULL = '--'
field_enhancer.enhance()
form_model_enhancer.enhance()

class SubmissionAnalyzer(object):
    def __init__(self, form_model, manager, request, filters):
        assert isinstance(form_model, FormModel)
        self.form_model = form_model
        self.manager = manager
        self.request = request
        self.filtered_submissions = filter_submissions(filters, self.form_model, self.manager)
        self.leading_part = None
        self.field_values = None

    def get_headers(self):
        return helper.get_headers(self.form_model)

    def get_subjects(self):
        if self.form_model.entity_defaults_to_reporter():  return []
        subjects =  [row[0] for row in self.leading_part if row[0][1] != '--']
        return sorted(list(set(subjects)))

    def get_data_senders(self):
        data_sender_col_index = 4 if self.form_model.entity_defaults_to_reporter() else 3
        data_sender_col_index = data_sender_col_index if self.form_model.has_report_period_question() else data_sender_col_index -1
        data_senders =  [row[data_sender_col_index] for row in self._get_leading_part()]
        return sorted(list(set(data_senders)))

    def get_raw_field_values(self):
        self.leading_part = self._get_leading_part()
        self.field_values = self.get_field_values()
        return [leading + remaining[1:] for leading, remaining in zip(self.leading_part, self.field_values)]

    def _get_leading_part(self):
        result = []
        rp_field = self.form_model.event_time_question
        is_first_element_needed = self.form_model.entity_type != ['reporter']
        for submission in self.filtered_submissions:
            data_sender = get_data_sender(self.manager, self.request.user, submission)
            submission_date = _to_str(submission.created)
            row = [submission_date, data_sender]
            if rp_field:
                reporting_period = case_insensitive_lookup(rp_field.code, submission.values) if rp_field else None
                reporting_period = _to_str(reporting_period, rp_field)
                row = [reporting_period] + row

            if is_first_element_needed:
                first_element = self._get_first_element_of_leading_part(submission)
                row = [first_element] + row
            result.append(row)
        return result

    def _get_first_element_of_leading_part(self, submission):
        short_code = case_insensitive_lookup(self.form_model.entity_question.code, submission.values)
        try:
            entity = get_by_short_code(self.manager, short_code, [self.form_model.entity_type[0]])
        except DataObjectNotFound:
            return NOT_AVAILABLE, short_code

        return entity.data['name']['value'], entity.short_code

    def get_field_values(self):
        field_values = [submission.values for submission in self.filtered_submissions]
        field_values_list = []
        for row in field_values:
            self.replace_option_with_real_answer_value(row)
            fields_ = [case_insensitive_lookup(field.code, row) for field in self.form_model.non_rp_fields()]
            field_values_list.append(fields_)
        return field_values_list

    def replace_option_with_real_answer_value(self, row):
        assert isinstance(row, dict)
        for question_code,question_value in row.iteritems():
            field = self.form_model.get_field_by_code(question_code)
            if isinstance(field,SelectField):
                row[question_code] = self.get_option_value_list(field, question_value)

    def get_option_value_list(self, field, question_value):
        if question_value is None: return []

        options = re.findall(r'[1-9]?[a-z]', question_value)
        return [field.get_value_by_option(option) for option in options ]

##
def get_formatted_values_for_list(values, tuple_sep = "\n", list_sep = ","):
    formatted_values = []
    for row in values:
        result = _format_row(list_sep, row, tuple_sep)
        formatted_values.append(list(result))
    return formatted_values

def _format_row(list_sep, row, tuple_sep):
    for each in row:
        if isinstance(each, tuple):
            assert len(each) >= 2
            new_val = "%s%s(%s)" % (each[0], tuple_sep, each[1]) if each[1] else each[0]
        elif isinstance(each, list):
            new_val = list_sep.join(each)
        elif each:
            new_val = each
        else:
            new_val = NULL
        yield new_val
