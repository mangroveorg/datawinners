from collections import OrderedDict, defaultdict
from datetime import datetime
import abc
from django.utils.translation import ugettext
from datawinners.enhancer import field_enhancer
from datawinners.main.utils import timebox
from mangrove.datastore.entity import get_by_short_code
from datawinners.project.data_sender_helper import  combine_channels_for_tuple, get_data_sender
from datawinners.project.filters import KeywordFilter
from datawinners.project.helper import format_dt_for_submission_log_page, case_insensitive_lookup, _to_str, NOT_AVAILABLE
from datawinners.project.submission_router import SubmissionRouter
from datawinners.project.submission_utils.submission_filter import SubmissionFilter
from mangrove.form_model.field import SelectField, DateField, ExcelDate
from mangrove.utils.types import is_sequence

field_enhancer.enhance()

def _override_value_if_not_present(value):
    return value if value else "--"


class SubmissionData(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, form_model, manager, org_id, header, submission_type, filters, keyword=None):
        self.header_class = header
        self.manager = manager
        self.form_model = form_model
        self.org_id = org_id
        self._data_senders = []
        self._subject_list = []
        self.keyword_filter = KeywordFilter(keyword if keyword else '')
        submissions = self._get_submissions_by_type(manager, form_model, submission_type)
        self.filtered_submissions = SubmissionFilter(filters, form_model).filter(submissions)
        self._init_values()

    def _get_submissions_by_type(self, manager, form_model, submission_type):
        submissions = SubmissionRouter().route(submission_type)(manager, form_model.form_code)
        if submission_type == SubmissionRouter.ERROR:
            return filter(lambda x: not x.status, submissions)
        return submissions

    def _init_values(self):
        leading_part = self.get_leading_part()
        raw_field_values = [leading + remaining[1:] for leading, remaining in
                            zip(leading_part, self._get_field_values())]

        self._raw_values = self.keyword_filter.filter(raw_field_values)
        if leading_part:
            self.leading_part_length = len(leading_part[0])

    def _get_submission_details(self, filtered_submissions):
        data_sender = self._get_data_sender(filtered_submissions)
        submission_date = format_dt_for_submission_log_page(filtered_submissions)
        rp = self._get_rp_for_leading_part(filtered_submissions)
        subject = self._get_subject_for_leading_part(filtered_submissions)
        return data_sender, rp, subject, submission_date

    def get_submission_details_for_excel(self, filtered_submissions):
        data_sender, reporting_date, subject, submission_date = self._get_submission_details(filtered_submissions)
        reporting_date_excel = self.form_model.get_field_by_code_and_rev(self.form_model.event_time_question.code,
            filtered_submissions.form_model_revision).formatted_field_values_for_excel(reporting_date)
        submission_date = ExcelDate(filtered_submissions.created, 'submission_date')
        return data_sender, reporting_date_excel, subject, submission_date

    def _get_data_sender(self, submission):
        for each in self._data_senders:
            if each[-1] == submission.source:
                return each
        else:
            data_sender = get_data_sender(self.manager, self.org_id, submission)
            self._data_senders.append(data_sender)
            return data_sender

    def get_data_senders(self):
        return combine_channels_for_tuple(self._data_senders)

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

    def _get_subject(self, submission):
        subject_code = case_insensitive_lookup(self.form_model.entity_question.code, submission.values)
        for each in self._subject_list:
            if each[-1] == subject_code:
                return each
        else:
            try:
                entity = get_by_short_code(self.manager, subject_code, [self.form_model.entity_type[0]])
                subject = entity.data['name']['value'], entity.short_code
            except Exception:
                subject = NOT_AVAILABLE, str(subject_code)

            self._subject_list.append(subject)
            return subject

    def _get_translated_submission_status(self, status):
        return ugettext('Success') if status else ugettext('Error')

    #  TODO : should be moved to utils
    def order_formatted_row(self, question_field_code, formatted_answers):
        if question_field_code.lower() not in eval(repr(formatted_answers.keys()).lower()):
            return ['--']
        else:
            for question_code, submitted_answer in formatted_answers.items():
                if question_code.lower() == question_field_code.lower():
                    if type(submitted_answer) is tuple:
                        lat, long = submitted_answer
                        return [_override_value_if_not_present(lat), _override_value_if_not_present(long)]
                    return [_override_value_if_not_present(submitted_answer)]

    def get_raw_values(self):
        return self._raw_values

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

    def get_subjects(self):
        return sorted(self._subject_list)

    def get_default_sort_order(self):
        default_sort_order = [[2, 'desc']]

        if self.form_model.event_time_question and self.form_model.entity_type != ['reporter']:
            default_sort_order = [[3, 'desc']]

        if self.form_model.event_time_question is None and self.form_model.entity_type == ['reporter']:
            default_sort_order = [[1, 'desc']]

        return default_sort_order

    def _init_statistics_result(self):
        result = OrderedDict()
        for each in self.form_model.fields:
            if isinstance(each, SelectField):
                result.setdefault(each.name, {"choices": defaultdict(int), "type": each.type, 'total': 0})
                for option in each.options:
                    result[each.name]['choices'][option['text']] = 0
        return result

    @abc.abstractmethod
    def get_leading_part(self):
        return

    @timebox
    @abc.abstractmethod
    def _get_field_values(self):
        pass
