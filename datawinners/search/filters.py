from babel.dates import format_datetime
import datetime
from mangrove.form_model.field import DateField

DATE_PICKER_WIDGET_DATE_FORMAT = '%d.%m.%Y'


class DateRangeFilter():
    def __init__(self, date_range):
        self.start_date, self.end_date = self._get_dates_from_request(date_range)

    def get_date_field_name(self):
        pass

    def get_persisted_date_format(self):
        pass

    def get_python_date_format(self, date_format):
        pass

    def _format_date(self, date_string, date_format, end_date=False):
        date = datetime.datetime.strptime(date_string.strip(), self.get_python_date_format(date_format))
        if end_date:
            date = date + datetime.timedelta(days=1)
        return format_datetime(date, date_format)

    def _get_dates_from_request(self, date_range):
        try:
            date_range_split = date_range.split('-')
            if len(date_range_split) == 1:
                return self._format_date(date_range_split[0], self.get_persisted_date_format()), self._format_date(
                    date_range_split[0], self.get_persisted_date_format(), end_date=True)
            return self._format_date(date_range_split[0], self.get_persisted_date_format()), self._format_date(
                date_range_split[1],
                self.get_persisted_date_format(), end_date=True)
        except Exception as e:
            return None, None

    def _get_date_range_filter_args(self, start, end):
        return {self.get_date_field_name() + '_value__range': [start, end]}

    def build_filter_query(self, query):
        if not self.start_date and not self.end_date:
            return query
        else:
            kwargs = self._get_date_range_filter_args(self.start_date, self.end_date)
            return query.filter(**kwargs)


class SubmissionDateRangeFilter(DateRangeFilter):
    def get_date_field_name(self):
        return "date"

    def get_persisted_date_format(self):
        return DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')

    def get_python_date_format(self, date):
        return '%d.%m.%Y'

class ReportingDateRangeFilter(SubmissionDateRangeFilter):
    def __init__(self, date_range, form_model):
        self.reporting_date_field = form_model.event_time_question
        SubmissionDateRangeFilter.__init__(self, date_range)

    def get_persisted_date_format(self):
        if self.reporting_date_field:
            return DateField.FORMAT_DATE_DICTIONARY.get(self.reporting_date_field.date_format)
        return None

    def get_date_field_name(self):
        return self.reporting_date_field.code

    def get_python_date_format(self, date):
        if self.reporting_date_field:
            return DateField.DATE_DICTIONARY.get(self.reporting_date_field.date_format)
        return None