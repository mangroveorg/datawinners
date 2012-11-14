#encoding=utf-8
from collections import OrderedDict
from django.utils.translation import ugettext
from main.utils import timebox
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import SelectField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.submissions import get_submissions
from project.filters import KeywordFilter
from project.helper import get_data_sender, _to_str, case_insensitive_lookup, NOT_AVAILABLE, DEFAULT_DATE_FORMAT
from enhancer import form_model_enhancer, field_enhancer
from utils import sorted_unique_list

NULL = '--'
field_enhancer.enhance()
form_model_enhancer.enhance()
SUCCESS_SUBMISSION_LOG_VIEW_NAME = "success_submission_log"

class SubmissionAnalyzer(object):
    def __init__(self, form_model, manager, request, filters, keyword=None):
        assert isinstance(form_model, FormModel)
        self.form_model = form_model
        self.manager = manager
        self.request = request
        submissions = get_submissions_with_timing(form_model, manager)
        self.filtered_submissions = filter_submissions(submissions, filters)
        self._data_senders = []
        self._subject_list = []
        self.keyword_filter = KeywordFilter(keyword if keyword else '')
        self.leading_part_length = 0
        self.filtered_leading_part = []
        self._init_raw_values()

    def get_raw_values(self):
        return self._raw_values

    def get_default_sort_order(self):
        default_sort_order = [[0, 'desc'],[2, 'desc']] if self.form_model.event_time_question else [[0, 'desc'],[1, 'desc']]
        if self.form_model.entity_type != ['reporter']:
            default_sort_order = [[1, 'desc'],[0,'desc']]
        return default_sort_order

    def get_headers(self):
        prefix = [ugettext("Submission Date"), ugettext("Data Sender")]
        prefix_types = [DEFAULT_DATE_FORMAT.lower(), '']
        if self.form_model.event_time_question:
            prefix = [ugettext("Reporting Period")] + prefix
            prefix_types = [self.form_model.event_time_question.date_format] + prefix_types

        if self.form_model.entity_type != ['reporter']:
            prefix = [ugettext(self.form_model.entity_type[0]).capitalize()] + prefix
            prefix_types = [''] + prefix_types

        field_ = [(field.label,
                   field.date_format if isinstance(field, DateField) else (
                   "gps" if isinstance(field, GeoCodeField)  else "")) for field in self.form_model.fields[1:] if
                                                                       not field.is_event_time_field]
        return prefix + [each[0] for each in field_], prefix_types + [each[1] for each in field_]

    def get_subjects(self):
        if self.form_model.entity_defaults_to_reporter():  return []
        subjects = [row[0] for row in self.filtered_leading_part if row[0][1] != NULL]
        return sorted(list(set(subjects)))

    def get_data_senders(self):
        return sorted_unique_list(each[-1] for each in self.filtered_leading_part)

    def get_analysis_statistics(self):
        if not self._raw_values: return []

        field_header = self.get_headers()[0][self.leading_part_length:]
        result = self._init_statistics_result()
        for row in self._raw_values:
            for idx, question_values in enumerate(row[self.leading_part_length:]):
                question_name = field_header[idx]
                if isinstance(self.form_model.get_field_by_name(question_name), SelectField) and question_values:
                    result[question_name]['total'] += 1
                    for each in question_values:
                        result[question_name]['choices'][each] += 1

        list_result = []
        for key, value in result.items():
            row = [key, value['type'], value['total'], []]
            sorted_value = sorted(value['choices'].items(), key=lambda t: (t[1] * -1, t[0]))
            for option, count in sorted_value:
                row[-1].append([option, count])
            list_result.append(row)
        return list_result

    @timebox
    def _init_raw_values(self):
        field_values = self._get_field_values()
        leading_part = self._get_leading_part()
        raw_field_values = [leading + remaining[1:] for leading, remaining in zip(leading_part, field_values)]
        self._raw_values = self.keyword_filter.filter(raw_field_values)
        if leading_part:
            self.leading_part_length = len(leading_part[0])
            self.filtered_leading_part = [raw_value_row[:self.leading_part_length] for raw_value_row in
                                          self._raw_values]

    @timebox
    def _get_leading_part(self):
        leading_part = []
        for submission in self.filtered_submissions:
            data_sender = self._get_data_sender(submission)
            submission_date = _to_str(submission.created)
            row = [submission_date, data_sender]
            row = self._update_leading_part_for_rp(row, submission)
            row = self._update_leading_part_for_project_type(row, submission)
            leading_part.append(row)

        return leading_part

    @timebox
    def _get_field_values(self):
        submission_values = [submission.values for submission in self.filtered_submissions]
        field_values = []
        for row in submission_values:
            self._replace_option_with_real_answer_value(row)
            fields_ = [case_insensitive_lookup(field.code, row) for field in self.form_model.non_rp_fields()]
            field_values.append(fields_)
        return field_values

    def _get_data_sender(self, submission):
        for each in self._data_senders:
            if each[-1] == submission.source:
                return each
        else:
            data_sender = get_data_sender(self.manager, self.request.user, submission)
            self._data_senders.append(data_sender)
            return data_sender

    def _get_subject(self, submission):
        subject_code = case_insensitive_lookup(self.form_model.entity_question.code, submission.values)
        for each in self._subject_list:
            if each[-1] == subject_code:
                return each
        else:
            try:
                entity = get_by_short_code(self.manager, subject_code, [self.form_model.entity_type[0]])
                subject = entity.data['name']['value'], entity.short_code
            except DataObjectNotFound:
                subject = NOT_AVAILABLE, subject_code

            self._subject_list.append(subject)
            return subject

    def _update_leading_part_for_rp(self, row, submission):
        rp_field = self.form_model.event_time_question
        if rp_field:
            reporting_period = case_insensitive_lookup(rp_field.code, submission.values)
            reporting_period = _to_str(reporting_period, rp_field)
            return [reporting_period] + row
        else:
            return row

    def _update_leading_part_for_project_type(self, row, submission):
        if  self.form_model.entity_defaults_to_reporter(): return row
        subject = self._get_subject(submission)
        return [subject] + row

    def _replace_option_with_real_answer_value(self, row):
        assert isinstance(row, dict)
        for question_code, question_value in row.iteritems():
            field = self.form_model.get_field_by_code(question_code)
            if isinstance(field, SelectField):
                row[question_code] = field.get_option_value_list(question_value)

    def _init_statistics_result(self):
        result = OrderedDict()
        for each in self.form_model.fields:
            if isinstance(each, SelectField):
                result.setdefault(each.name, {"choices": {}, "type": each.type, 'total': 0})
                for option in each.options:
                    opt_text = option['text']
                    result[each.name]['choices'][opt_text] = 0
        return result


def get_formatted_values_for_list(values, tuple_format='%s<span class="small_grey">%s</span>', list_delimiter=', '):
    formatted_values = []
    for row in values:
        result = _format_row(row, tuple_format, list_delimiter)
        formatted_values.append(list(result))
    return formatted_values


def _format_row(row, tuple_format, list_delimiter):
    for each in row:
        if isinstance(each, tuple):
            new_val = tuple_format % (each[0], each[1]) if each[1] else each[0]
        elif isinstance(each, list):
            new_val = list_delimiter.join(each)
        elif each:
            new_val = each
        else:
            new_val = NULL
        yield new_val

@timebox
def filter_submissions(submissions, filters):
    to_lowercase_submission_keys(submissions)
    for filter in filters:
        submissions = filter.filter(submissions)
    return submissions

def to_lowercase_submission_keys(submissions):
    for submission in submissions:
        values = submission.values
        submission._doc.values = dict((k.lower(), v) for k,v in values.iteritems())

@timebox
def get_submissions_with_timing(form_model, manager):
    return get_submissions(manager, form_model.form_code, None, None, view_name=SUCCESS_SUBMISSION_LOG_VIEW_NAME)
