import unittest
import elasticutils
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import DateField
from mock import Mock, PropertyMock
from datawinners.search.filters import SubmissionDateRangeFilter, ReportingDateRangeFilter
from mangrove.form_model.form_model import FormModel


class TestSubmissionFilter(unittest.TestCase):
    def test_get_formatted_date(self):
        submission_date_format = DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')

        result = SubmissionDateRangeFilter('a-a')._format_date('28.11.2013', submission_date_format)
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


class TestReportingDateFilter(unittest.TestCase):
    def test_should_return_back_query_if_no_reporting_period_question(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = Mock(spec=FormModel)
        type(mock_form_model).event_time_question = PropertyMock(return_value=None)
        result = ReportingDateRangeFilter(None, mock_form_model).build_filter_query(mock_query)
        self.assertEquals(result, mock_query)

    def test_should_not_call_query_with_start_and_end_date_for_invalid_date_range(self):
        mock_query = Mock(spec=elasticutils.S)
        result = SubmissionDateRangeFilter('All Periods').build_filter_query(mock_query)
        self.assertEquals(result, mock_query)

    def test_should_build_query_with_start_and_end_date(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = Mock(spec=FormModel)
        type(mock_form_model).event_time_question = PropertyMock(
            return_value=DateField(name='rp', code='rp', label='rp', date_format='dd.mm.yyyy',
                                   ddtype=Mock(spec=DataDictType)))
        ReportingDateRangeFilter('21.11.2013-28.11.2013', mock_form_model).build_filter_query(mock_query)
        mock_query.filter.assert_called_with(rp_value__range=['21.11.2013', '29.11.2013'])

    def test_should_call_query_match_for_current_day(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = Mock(spec=FormModel)
        type(mock_form_model).event_time_question = PropertyMock(
            return_value=DateField(name='rp', code='rp', label='rp', date_format='dd.mm.yyyy',
                                   ddtype=Mock(spec=DataDictType)))
        today = "26.11.2013"
        ReportingDateRangeFilter(today, mock_form_model).build_filter_query(mock_query)
        mock_query.filter.assert_called_with(rp_value__range=['26.11.2013', '27.11.2013'])
