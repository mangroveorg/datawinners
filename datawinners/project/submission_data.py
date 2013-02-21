from collections import OrderedDict, defaultdict
import abc
from django.utils.translation import ugettext
from datawinners.enhancer import field_enhancer
from datawinners.main.utils import timebox
from mangrove.datastore.entity import get_by_short_code
from datawinners.project.data_sender_helper import DataSenderHelper, combine_channels_for_tuple, get_data_sender
from datawinners.project.filters import KeywordFilter
from datawinners.project.helper import format_dt_for_submission_log_page, case_insensitive_lookup, _to_str, NOT_AVAILABLE
from datawinners.project.submission_router import SubmissionRouter
from datawinners.project.submission_utils.submission_filter import SubmissionFilter
from mangrove.form_model.field import SelectField, IntegerField, GeoCodeField, DateField
from mangrove.utils.types import is_sequence

field_enhancer.enhance()

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
        self.submissions = self._get_submissions_by_type(manager, form_model, submission_type)
        self.filtered_submissions = SubmissionFilter(filters, form_model).filter(self.submissions)


    def _get_submissions_by_type(self, manager, form_model, submission_type):
        submissions = SubmissionRouter().route(submission_type)(manager, form_model.form_code)
        if submission_type == SubmissionRouter.ERROR:
            return filter(lambda x: not x.status, submissions)
        return submissions

    @timebox
    @abc.abstractmethod
    def _init_raw_values(self):
        return

    def populate_submission_data(self, leading_part):
        raw_field_values = [leading + remaining[1:] for leading, remaining in zip(leading_part,
            self._get_field_values())]
        self._raw_values = self.keyword_filter.filter(raw_field_values)
        if leading_part:
            self.leading_part_length = len(leading_part[0])
            self.filtered_leading_part = [raw_value_row[:self.leading_part_length] for raw_value_row in
                                          self._raw_values]

    def populate_submission_data_for_excel(self, leading_part):
        raw_field_values = [leading + remaining[1:] for leading, remaining in zip(leading_part,
            self._get_field_values_for_excel())]
        self._raw_values = self.keyword_filter.filter(raw_field_values)
        if leading_part:
            self.leading_part_length = len(leading_part[0])
            self.filtered_leading_part = [raw_value_row[:self.leading_part_length] for raw_value_row in
                                          self._raw_values]

    def _get_submission_details(self, submission):
        data_sender = self._get_data_sender(submission)
        submission_date = format_dt_for_submission_log_page(submission)
        rp = self._get_rp_for_leading_part(submission)
        subject = self._get_subject_for_leading_part(submission)
        return data_sender, rp, subject, submission_date

    @abc.abstractmethod
    def get_leading_part(self):
        return

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


    @timebox
    def _get_field_values(self):
        submission_values = [(submission.form_model_revision, submission.values) for submission in self.filtered_submissions]
        field_values = []
        for row in submission_values:
            self._replace_option_with_real_answer_value(row)
            fields_ = [case_insensitive_lookup(field.code, row[-1]) for field in self.form_model.non_rp_fields_by()]
            field_values.append(fields_)

        return field_values

    @timebox
    def _get_field_values_for_excel(self):
        submission_values = [(submission.form_model_revision, submission.values) for submission in self.filtered_submissions]
        field_values = []
        for row in submission_values:
            fields_ = []
            formatted_row = self._format_field_values_for_excel(row)
            for field in self.form_model.non_rp_fields_by():
                fields_.extend(self._order_formatted_row(field.code, formatted_row))
            field_values.append(fields_)
        return field_values

    def _order_formatted_row(self,search_key,formatted_row):

        for key, value in formatted_row.items():
            if search_key.lower()!='gps':
                if key.lower()==search_key.lower():
                    return [value]
                else:
                    pass
            else:
                return [formatted_row['gps_lat'],formatted_row['gps_long']]

    def _format_field_values_for_excel(self, row):
        changed_row = dict()
        for question_code, question_value in row[-1].iteritems():
            field = self.form_model.get_field_by_code_and_rev(question_code, row[0])
            if isinstance(field, SelectField):
                row[-1][question_code] = field.get_option_value_list(question_value)
                changed_row[question_code] = row[-1][question_code]
            elif isinstance(field, IntegerField):
                row[-1][question_code] = float(question_value)
                changed_row[question_code] = row[-1][question_code]
            elif isinstance(field, GeoCodeField):
                formatted_question_value = question_value.replace(',',' ')
                changed_row['gps_lat'] = formatted_question_value.split(' ')[0]
                changed_row['gps_long'] = formatted_question_value.split(' ')[1]
            elif isinstance(field,DateField):
                row[-1][question_code] = _to_str(question_value,field)
                changed_row[question_code] = row[-1][question_code]
            else:
                changed_row[question_code] = question_value
        return changed_row

    def _replace_option_with_real_answer_value(self, row):
        assert isinstance(row[-1], dict)
        for question_code, question_value in row[-1].iteritems():
            field = self.form_model.get_field_by_code_and_rev(question_code, row[0])
            if isinstance(field, SelectField):
                row[-1][question_code] = field.get_option_value_list(question_value)

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

