from babel.dates import format_datetime
import datetime
from mangrove.form_model.field import DateField


class DateRangeFilter():
    def __init__(self, date_range):
        self.start, self.end = self._get_dates_from_request(date_range)

    def get_date_field_name(self):
        pass

    def get_persisted_date_format(self):
        pass

    @staticmethod
    def _format_date(date_string, date_format, end_date=False):
        date = datetime.datetime.strptime(date_string.strip(), '%d.%m.%Y')
        if end_date:
            date = date + datetime.timedelta(days=1)
        return format_datetime(date, date_format)

    @staticmethod
    def _get_dates_from_request(date_range):
        if not date_range or date_range == 'All Dates' or date_range == 'All Periods':
            return None, None

        date_range_split = date_range.split('-')
        if len(date_range_split) == 1:
            return date_range_split[0], None
        return date_range_split

    def _get_date_range_filter_args(self, start, end):
        return {
            self.get_date_field_name() + '_value__range': [self._format_date(start, self.get_persisted_date_format()),
                                                           self._format_date(end, self.get_persisted_date_format(),
                                                                             end_date=True)]}

    def build_filter_query(self, query):
        if not self.get_persisted_date_format():
            return query

        if self.start and self.end:
            kwargs = self._get_date_range_filter_args(self.start, self.end)
            return query.filter(**kwargs)

        elif self.start and not self.end:
            kwargs = self._get_date_range_filter_args(self.start, self.start)
            return query.filter(**kwargs)

        else:
            return query


class SubmissionDateRangeFilter(DateRangeFilter):
    def get_date_field_name(self):
        return "date"

    def get_persisted_date_format(self):
        return DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')


class ReportingDateRangeFilter(SubmissionDateRangeFilter):
    def __init__(self, date_range, form_model):
        SubmissionDateRangeFilter.__init__(self, date_range)
        self.reporting_date_field = form_model.event_time_question

    def get_persisted_date_format(self):
        if self.reporting_date_field:
            return DateField.FORMAT_DATE_DICTIONARY.get(self.reporting_date_field.date_format)
        return None

    def get_date_field_name(self):
        return self.reporting_date_field.code

