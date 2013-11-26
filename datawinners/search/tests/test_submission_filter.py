import unittest
import elasticutils
from mangrove.form_model.field import DateField
from mock import Mock
from datawinners.search.filters import SubmissionDateRangeFilter


class TestSubmissionFilter(unittest.TestCase):
    def test_get_formatted_date(self):
        submission_date_format = DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')

        result = SubmissionDateRangeFilter('a-a').format_date('28.11.2013', submission_date_format)
        self.assertEquals('Nov. 28, 2013, 12:00 AM', result)

    def test_should_build_query_with_start_and_end_date(self):
        mock_query = Mock(spec=elasticutils.S)
        SubmissionDateRangeFilter('21.11.2013-28.11.2013').build_filter_query(mock_query)
        mock_query.filter.assert_called_with(date_value__range=['Nov. 21, 2013, 12:00 AM', 'Nov. 29, 2013, 12:00 AM'])

    def test_should_not_call_query_with_start_and_end_date_for_invalid_date_range(self):
        mock_query = Mock(spec=elasticutils.S)
        result = SubmissionDateRangeFilter('All Dates').build_filter_query(mock_query)
        self.assertEquals(result, mock_query)


    def test_should_call_query_match_for_current_day(self):
        mock_query = Mock(spec=elasticutils.S)
        today = "26.11.2013"
        SubmissionDateRangeFilter(today).build_filter_query(mock_query)
        mock_query.filter.assert_called_with(date_value__range=['Nov. 26, 2013, 12:00 AM', 'Nov. 27, 2013, 12:00 AM'])