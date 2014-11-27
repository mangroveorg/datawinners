import datetime

from babel.dates import format_datetime
from pyes import RangeQuery
from pyes.utils import ESRange
from datawinners.accountmanagement.localized_time import convert_local_to_utc

from datawinners.search.index_utils import es_questionnaire_field_name, es_submission_meta_field_name
from datawinners.search.submission_index_meta_fields import ES_SUBMISSION_FIELD_DATE
from mangrove.form_model.field import DateField


DATE_PICKER_WIDGET_DATE_FORMAT = '%d.%m.%Y'


class DateRangeFilter(object):
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
            date = date + datetime.timedelta(hours=23, minutes=59)
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
        return start, end

    def build_filter_query(self):
        if not self.start_date and not self.end_date:
            return None
        else:
            start, end = self._get_date_range_filter_args(self.start_date, self.end_date)
            return RangeQuery(qrange=
                              ESRange(field=self.get_date_field_name(), from_value=start, to_value=end,
                                      include_lower=True,
                                      include_upper=True))


class SubmissionDateRangeFilter(DateRangeFilter):
    def __init__(self, date_range, local_time_delta):
        super(SubmissionDateRangeFilter, self).__init__(date_range)
        self.local_time_delta = local_time_delta

    def _get_date_range_filter_args(self, start, end):
        date_format = "%b. %d, %Y, %I:%M %p"
        start_local_date_time_str = convert_local_to_utc(start, self.local_time_delta, date_format).strftime(
            date_format)
        end_local_date_time_str = convert_local_to_utc(end, self.local_time_delta, date_format).strftime(date_format)

        return super(SubmissionDateRangeFilter, self)._get_date_range_filter_args(start_local_date_time_str,
                                                                                  end_local_date_time_str)

    def get_date_field_name(self):
        return es_submission_meta_field_name(ES_SUBMISSION_FIELD_DATE) + "_value"

    def get_persisted_date_format(self):
        return DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')

    def get_python_date_format(self, date):
        return '%d.%m.%Y'


class DateQuestionRangeFilter(DateRangeFilter):
    def __init__(self, date_range, form_model, date_question_code):
        self.date_field = form_model.get_field_by_code(date_question_code)
        self.form_model = form_model
        DateRangeFilter.__init__(self, date_range)

    def get_persisted_date_format(self):
        if self.date_field:
            return DateField.FORMAT_DATE_DICTIONARY.get(self.date_field.date_format)
        return None

    def get_date_field_name(self):
        # Assumption is that date filters won't appear for dates questions within repeat fields
        return es_questionnaire_field_name(self.date_field.code, self.form_model.id,
                                           self.date_field.parent_field_code) + "_value"

    def get_python_date_format(self, date):
        if self.date_field:
            return DateField.DATE_DICTIONARY.get(self.date_field.date_format)
        return None