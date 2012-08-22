from datetime import datetime
from mangrove.form_model.field import DateField


class ReportPeriodFilter(object):
    def __init__(self, question_name=None, period=None, question_format="dd.mm.yyyy"):
        self.question_name = question_name
        self.period = period
        self.question_format = question_format


    def filter(self, submission_logs):
        assert self.question_name

        self.form_code = None if not len(submission_logs) else submission_logs[0].form_code

        return filter(lambda x: self.withinReportPeriod(x.values), submission_logs)

    def withinReportPeriod(self, values):
        report_time = self.parseDate(values[self.question_name])
        return self.parseDate(self.period['start']) <= report_time <= self.parseDate(self.period['end'])

    def parseDate(self, dateString):
        return datetime.strptime(dateString, DateField.get_datetime_format(self.question_format))
