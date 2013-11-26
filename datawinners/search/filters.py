from babel.dates import format_datetime
import datetime
from mangrove.form_model.field import DateField


class SubmissionDateRangeFilter():
    def __init__(self, date_range):
        self.submission_date_format = DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')
        self.start, self.end = self.get_dates(date_range)

    def build_filter_query(self, query):
        if self.start and self.end:
            return query.filter(date_value__range=[self.format_date(self.start, self.submission_date_format),
                                                   self.format_date(self.end, self.submission_date_format,
                                                                    end_date=True)])
        elif self.start and not self.end:
            return query.filter(date_value__range=[self.format_date(self.start, self.submission_date_format),
                                                   self.format_date(self.start, self.submission_date_format,
                                                                    end_date=True)])

            # return query.query(date__text_phrase=self.format_date(self.start, 'MMM. dd, yyyy'))
        else:
            return query

    def format_date(self, date_string, date_format, end_date=False):
        date = datetime.datetime.strptime(date_string.strip(), '%d.%m.%Y')
        if end_date:
            date = date + datetime.timedelta(days=1)
        return format_datetime(date, date_format)

    def get_dates(self, date_range):
        if date_range == '' or date_range == 'All Dates':
            return None, None

        date_range_split = date_range.split('-')
        if len(date_range_split) == 1:
            return date_range_split[0], None
        return date_range_split