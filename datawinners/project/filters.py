from datetime import datetime, timedelta
from dateutil.parser import parse
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from mangrove.form_model.field import DateField, ExcelDate
from mangrove.utils.types import is_sequence


class ReportPeriodFilter(object):
    def __init__(self, question_name=None, period=None, date_format="dd.mm.yyyy"):
        assert isinstance(period, dict)
        self.rp_question_name = question_name
        self.date_format = date_format
        self.start_time = self._parseDate(period['start'])
        self.end_time = self._parseDate(period['end'])

    def filter(self, survey_responses):
        assert self.rp_question_name

        self.form_code = None if not len(survey_responses) else survey_responses[0].form_code

        return filter(lambda x: self._withinReportPeriod(x.values), survey_responses)

    def _withinReportPeriod(self, values):
        try:
            report_time = self._parseDate(values[self.rp_question_name])
        except ValueError:
            return False

        return self.start_time <= report_time <= self.end_time

    def _parseDate(self, dateString):
        return datetime.strptime(dateString.strip(), DateField.DATE_DICTIONARY.get(self.date_format))

class SubjectFilter(object):
    def __init__(self, entity_question_code, subject_ids):
        self.entity_question_code = entity_question_code
        self.subject_ids = subject_ids.split(',')

    def filter(self, survey_responses):
        assert self.entity_question_code
        assert is_sequence(self.subject_ids)

        return filter(lambda x: self._with_subject(x.values), survey_responses)

    def _with_subject(self, values):
        return values.get(self.entity_question_code) in self.subject_ids


class DataSenderFilter(object):
    def __init__(self, survey_response_sources):
        self.survey_response_sources = survey_response_sources.split(',')

    def filter(self, survey_responses):
        return filter(lambda x: self._with_reporter_uid(x), survey_responses)

    def _with_reporter_uid(self, survey_response):
        reporter_uid = 'TEST' if survey_response.origin == TEST_REPORTER_MOBILE_NUMBER else survey_response.owner_uid
        return reporter_uid in self.survey_response_sources


class SurveyResponseDateFilter(object):
    def __init__(self, period, date_format="%d.%m.%Y %H:%M:%S %z"):
        assert isinstance(period, dict)
        self.date_format = date_format
        self.start_time = self._parseDate(period['start'])
        self.end_time = self._parseDate(period['end']) + timedelta(days=1)

    def filter(self, survey_responses):
        return filter(lambda x: self._in(x), survey_responses)

    def _in(self, survey_response):
        return self.start_time <= survey_response.submitted_on < self.end_time

    def _parseDate(self, dateString):
        return parse(dateString.strip() + " 00:00:00+0000", dayfirst=True)

class KeywordFilter(object):
    def __init__(self, keyword):
        self.keyword = keyword.lower()

    def filter(self, rows):
        if not self.keyword.strip():
            return rows
        return filter(lambda row: exists(self.contains, row[1:], True), rows)

    def contains(self, i):
        #Formatted values for xcel will hv Integerfields as float
        #Hence str is used .
        if isinstance(i,float) : i = str(i)
        if isinstance(i,ExcelDate) : i = i.date_as_string()
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
        if is_sequence(i):
            if len(i) ==3: i = i[:2]
            result.extend(i)
        else: result.append(i)
    return result