from datetime import datetime, timedelta
from dateutil.parser import parse
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from mangrove.form_model.field import DateField
from mangrove.utils.types import is_sequence


class ReportPeriodFilter(object):
    def __init__(self, question_name=None, period=None, date_format="dd.mm.yyyy"):
        assert isinstance(period, dict)
        self.rp_question_name = question_name
        self.date_format = date_format
        self.start_time = self._parseDate(period['start'])
        self.end_time = self._parseDate(period['end'])

    def filter(self, submission_logs):
        assert self.rp_question_name

        self.form_code = None if not len(submission_logs) else submission_logs[0].form_code

        return filter(lambda x: self._withinReportPeriod(x.values), submission_logs)

    def _withinReportPeriod(self, values):
        try:
            report_time = self._parseDate(values[self.rp_question_name])
        except ValueError:
            return False

        return self.start_time <= report_time <= self.end_time

    def _parseDate(self, dateString):
        return datetime.strptime(dateString.strip(), DateField.get_datetime_format(self.date_format))

class SubjectFilter(object):
    def __init__(self, entity_question_code, subject_ids):
        self.entity_question_code = entity_question_code
        self.subject_ids = subject_ids.split(',')

    def filter(self, submission_logs):
        assert self.entity_question_code
        assert is_sequence(self.subject_ids)

        return filter(lambda x: self._with_subject(x.values), submission_logs)

    def _with_subject(self, values):
        return values.get(self.entity_question_code) in self.subject_ids


class DataSenderFilter(object):
    def __init__(self, submission_sources):
        self.submission_sources = submission_sources.split(',')

    def filter(self, submission_logs):
        return filter(lambda x: self._with_source(x), submission_logs)

    def _with_source(self, submission):
        source = 'TEST' if submission.source == TEST_REPORTER_MOBILE_NUMBER else submission.source
        return source in self.submission_sources


class SubmissionDateFilter(object):
    def __init__(self, period, date_format="%d.%m.%Y %H:%M:%S %z"):
        assert isinstance(period, dict)
        self.date_format = date_format
        self.start_time = self._parseDate(period['start'])
        self.end_time = self._parseDate(period['end']) + timedelta(days=1)

    def filter(self, submission_logs):
        return filter(lambda x: self._in(x), submission_logs)

    def _in(self, submission):
        return self.start_time <= submission.created < self.end_time

    def _parseDate(self, dateString):
        return parse(dateString.strip() + " 00:00:00+0000", dayfirst=True)

class KeywordFilter(object):
    def __init__(self, keyword):
        self.keyword = keyword.lower()

    def filter(self, rows):
        if not self.keyword.strip():
            return rows
        return filter(lambda row: exists(self.contains, row, True), rows)

    def contains(self, i):
        return i is not None and self.keyword in i.lower()

def exists(func, list, need_flatten=False):
    assert callable(func)
    assert is_sequence(list)

    sequence = flatten(list) if need_flatten else list
    for i in sequence:
        if func(i): return True
    return False

def flatten(less_than_two_layers_list):
    """
        Only two layers list is supported.
    """
    result = []
    for i in less_than_two_layers_list:
        if is_sequence(i): result.extend(i)
        else: result.append(i)
    return result