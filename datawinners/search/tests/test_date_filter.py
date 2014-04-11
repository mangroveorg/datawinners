import unittest
import elasticutils
from mangrove.form_model.field import DateField
from mock import Mock, PropertyMock, MagicMock
from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from mangrove.form_model.form_model import FormModel


class TestSubmissionFilter(unittest.TestCase):
    def test_get_formatted_date(self):
        submission_date_format = DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')

        result = SubmissionDateRangeFilter('a-a')._format_date('28.11.2013', submission_date_format)
        self.assertEquals('Nov. 28, 2013, 12:00 AM', result)

    def test_should_build_query_with_start_and_end_date(self):
        mock_query = Mock(spec=elasticutils.S)
        SubmissionDateRangeFilter('21.11.2013-28.11.2013').build_filter_query(mock_query)
        mock_query.filter.assert_called_with(date_value__range=['Nov. 21, 2013, 12:00 AM', 'Nov. 28, 2013, 11:59 PM'])

    def test_should_not_call_query_with_start_and_end_date_for_invalid_date_range(self):
        mock_query = Mock(spec=elasticutils.S)
        result = SubmissionDateRangeFilter('All Dates').build_filter_query(mock_query)
        self.assertEquals(result, mock_query)


    def test_should_call_query_match_for_current_day(self):
        mock_query = Mock(spec=elasticutils.S)
        today = "26.11.2013"
        SubmissionDateRangeFilter(today).build_filter_query(mock_query)
        mock_query.filter.assert_called_with(date_value__range=['Nov. 26, 2013, 12:00 AM', 'Nov. 26, 2013, 11:59 PM'])


class TestSubmissionDateFilter(unittest.TestCase):
    def test_should_not_call_query_with_start_and_end_date_for_invalid_date_range(self):
        mock_query = Mock(spec=elasticutils.S)
        result = SubmissionDateRangeFilter('All Periods').build_filter_query(mock_query)
        self.assertEquals(result, mock_query)


class TestDateQuestionFilter(unittest.TestCase):

    def test_should_build_query_with_start_and_end_date_for_dd_mm_yy_format(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='Some date question', date_format='dd.mm.yyyy')
        mock_form_model.id = 'form_id'
        DateQuestionRangeFilter('21.11.2013-28.11.2013', mock_form_model, 'q1').build_filter_query(mock_query)
        mock_query.filter.assert_called_with(form_id_q1_value__range=['21.11.2013', '28.11.2013'])

    def test_should_build_query_with_start_and_end_date_for_mm_dd_yy_format(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='Some date question', date_format='mm.dd.yyyy')
        mock_form_model.id = 'form_id'
        DateQuestionRangeFilter('11.21.2013-11.28.2013', mock_form_model, 'q1').build_filter_query(mock_query)
        mock_query.filter.assert_called_with(form_id_q1_value__range=['11.21.2013', '11.28.2013'])

    def test_should_build_query_with_start_and_end_date_for_mm_yyyy_format(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='q1', date_format='mm.yyyy')
        mock_form_model.id = 'form_id'
        DateQuestionRangeFilter('11.2013-09.2013', mock_form_model, 'q1').build_filter_query(mock_query)
        mock_query.filter.assert_called_with(form_id_q1_value__range=['11.2013', '09.2013'])

    def test_should_call_query_match_for_current_day(self):
        mock_query = Mock(spec=elasticutils.S)
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='q1', date_format='dd.mm.yyyy')
        mock_form_model.id = 'form_id'
        today = "26.11.2013"
        DateQuestionRangeFilter(today, mock_form_model, 'q1').build_filter_query(mock_query)
        mock_query.filter.assert_called_with(form_id_q1_value__range=['26.11.2013', '26.11.2013'])
