from datetime import datetime
from mangrove.form_model.field import DateField
from mangrove.utils.types import is_sequence


class ReportPeriodFilter(object):
    def __init__(self, question_name=None, period=None, question_format="dd.mm.yyyy"):
        assert isinstance(period, dict)
        self.rp_question_name = question_name
        self.question_format = question_format
        self.start_time = self._parseDate(period['start'])
        self.end_time = self._parseDate(period['end'])

    def filter(self, submission_logs):
        assert self.rp_question_name

        self.form_code = None if not len(submission_logs) else submission_logs[0].form_code

        return filter(lambda x: self._withinReportPeriod(x.values), submission_logs)

    def _withinReportPeriod(self, values):
        report_time = self._parseDate(values[self.rp_question_name])

        return self.start_time <= report_time <= self.end_time

    def _parseDate(self, dateString):
        return datetime.strptime(dateString.strip(), DateField.get_datetime_format(self.question_format))

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




