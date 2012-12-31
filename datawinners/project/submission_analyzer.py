#encoding=utf-8
from collections import OrderedDict, defaultdict
from django.utils.translation import ugettext
from main.utils import timebox
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import SelectField
from mangrove.form_model.form_model import FormModel
from mangrove.utils.types import is_sequence
from project.Header import Header, SubmissionsPageHeader
from project.analysis_result import AnalysisResult
from project.data_sender_helper import DataSenderHelper
from project.filters import KeywordFilter
from project.helper import  _to_str, case_insensitive_lookup, NOT_AVAILABLE, format_dt_for_submission_log_page
from enhancer import field_enhancer
from project.submission_utils.submission_formatter import SubmissionFormatter


NULL = '--'
field_enhancer.enhance()

class SubmissionAnalyzer(object):
    def __init__(self, form_model, manager, org_id, submissions, keyword=None, is_for_submission_page=False):
        assert isinstance(form_model, FormModel)
        self.header_class = SubmissionsPageHeader if is_for_submission_page else Header
        self.manager = manager
        self.form_model = form_model
        self.org_id = org_id
        self.submissions = submissions
        self._data_senders = []
        self._subject_list = []
        self.keyword_filter = KeywordFilter(keyword if keyword else '')
        self.leading_part_length = 0
        self.filtered_leading_part = []
        self._init_raw_values()


    def analyse(self):
        header = self.get_header()
        field_values = SubmissionFormatter().get_formatted_values_for_list(self.get_raw_values())
        analysis_statistics = self.get_analysis_statistics()
        data_sender_list = self.get_data_senders()
        subject_lists = self.get_subjects()
        default_sort_order = self.get_default_sort_order()

        return AnalysisResult(header, field_values, analysis_statistics, data_sender_list, subject_lists,default_sort_order)

    def get_raw_values(self):
        return self._raw_values

    def get_header(self):
        return self.header_class(self.form_model)

    def get_default_sort_order(self):
        default_sort_order = [[1, 'desc'], [3, 'asc']] if self.form_model.event_time_question else [[1, 'desc'],
                                                                                                    [2, 'asc']]
        if self.form_model.entity_type != ['reporter']:
            default_sort_order = [[2, 'desc'], [1, 'asc']]

        return default_sort_order

    def get_subjects(self):
        return sorted(self._subject_list)

    def get_data_senders(self):
        return sorted(self._data_senders)

    @timebox
    def get_analysis_statistics(self):
        if not self._raw_values: return []

        field_header = self.header_class(self.form_model).header_list[self.leading_part_length:]

        result = self._init_statistics_result()
        for row in self._raw_values:
            for idx, question_values in enumerate(row[self.leading_part_length:]):
                question_name = field_header[idx]
                if isinstance(self.form_model.get_field_by_name(question_name), SelectField) and question_values:
                    result[question_name]['total'] += 1
                    if is_sequence(question_values):
                        for each in question_values:
                            result[question_name]['choices'][each] += 1
                    else:
                        result[question_name]['choices'][question_values] += 1

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
        leading_part = self._get_leading_part()
        raw_field_values = [leading + remaining[1:] for leading, remaining in zip(leading_part,
            self._get_field_values())]
        self._raw_values = self.keyword_filter.filter(raw_field_values)
        if leading_part:
            self.leading_part_length = len(leading_part[0])
            self.filtered_leading_part = [raw_value_row[:self.leading_part_length] for raw_value_row in
                                          self._raw_values]

    def _get_leading_part_for_analysis_page(self, submission):
        data_sender = self._get_data_sender(submission)
        submission_date = _to_str(submission.created)
        rp = self._get_rp_for_leading_part(submission)
        subject = self._get_subject_for_leading_part(submission)
        return filter(lambda x: x, [submission.id, subject, rp, submission_date, data_sender])

    def _get_leading_part_for_submission_page(self, submission):
        data_sender = self._get_data_sender(submission)
        submission_date = format_dt_for_submission_log_page(submission)
        rp = self._get_rp_for_leading_part(submission)
        subject = self._get_subject_for_leading_part(submission)
        status = self._get_translated_submission_status(submission.status)
        return filter(lambda x: x, [submission.id, data_sender, submission_date, status, rp, subject])

    @timebox
    def _get_leading_part(self):
        leading_part = []
        for submission in self.submissions:
            if self.header_class == Header:
                row = self._get_leading_part_for_analysis_page(submission)
            else:
                row = self._get_leading_part_for_submission_page(submission)
            leading_part.append(row)

        return leading_part

    def _get_translated_submission_status(self, status):
        return ugettext('Success') if status else ugettext('Error')

    @timebox
    def _get_field_values(self):
        submission_values = [(submission.form_model_revision, submission.values) for submission in self.submissions]
        field_values = []
        for row in submission_values:
            self._replace_option_with_real_answer_value(row)
            fields_ = [case_insensitive_lookup(field.code, row[-1]) for field in self.form_model.non_rp_fields_by()]
            field_values.append(fields_)

        return field_values

    def _get_data_sender(self, submission):
        for each in self._data_senders:
            if each[-1] == submission.source:
                return each
        else:
            data_sender = DataSenderHelper(self.manager, self.form_model.form_code).get_data_sender(self.org_id, submission)
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

    def _get_rp_for_leading_part(self, submission):
        rp_field = self.form_model.event_time_question
        if rp_field:
            reporting_period = case_insensitive_lookup(rp_field.code, submission.values)
            return _to_str(reporting_period, rp_field)
        else:
            return None

    def _get_subject_for_leading_part(self, submission):
        if  not self.form_model.entity_defaults_to_reporter():
            return self._get_subject(submission)
        else:
            return None

    def _replace_option_with_real_answer_value(self, row):
        assert isinstance(row[-1], dict)
        for question_code, question_value in row[-1].iteritems():
            field = self.form_model.get_field_by_code_and_rev(question_code, row[0])
            if isinstance(field, SelectField):
                row[-1][question_code] = field.get_option_value_list(question_value)

    def _init_statistics_result(self):
        result = OrderedDict()
        for each in self.form_model.fields:
            if isinstance(each, SelectField):
                result.setdefault(each.name, {"choices": defaultdict(int), "type": each.type, 'total': 0})
                for option in each.options:
                    result[each.name]['choices'][option['text']] = 0
        return result
