import unittest
import elasticutils
from mangrove.form_model.field import DateField
from mock import Mock, PropertyMock, MagicMock
from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from mangrove.form_model.form_model import FormModel


class TestSubmissionFilter(unittest.TestCase):
    def test_get_formatted_date(self):
        submission_date_format = DateField.FORMAT_DATE_DICTIONARY.get('submission_date_format')

        formatted_date = SubmissionDateRangeFilter('a-a', ('+', 0, 0))._format_date('28.11.2013',
                                                                                    submission_date_format)

        self.assertEquals('Nov. 28, 2013, 12:00 AM', formatted_date)

    def test_should_build_query_with_start_and_end_date(self):
        actual_query = SubmissionDateRangeFilter('21.11.2013-28.11.2013', ('-', 1, 30)).build_filter_query()
        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'date_value': {'gte': 'Nov. 21, 2013, 01:30 AM',
                                                       'lte': 'Nov. 29, 2013, 01:29 AM'}}})

    def test_should_call_query_match_for_current_day(self):
        today = "26.11.2013"
        actual_query = SubmissionDateRangeFilter(today, ('+', 0, 0)).build_filter_query()
        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'date_value': {'gte': 'Nov. 26, 2013, 12:00 AM',
                                                       'lte': 'Nov. 26, 2013, 11:59 PM'}}})

    def test_should_return_range_with_local_to_utc_conversion(self):
        actual_query = SubmissionDateRangeFilter('21.11.2013-28.11.2013', ('+', 1, 30)).build_filter_query()
        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'date_value': {'gte': 'Nov. 20, 2013, 10:30 PM',
                                                       'lte': 'Nov. 28, 2013, 10:29 PM'}}})

    def test_should_return_no_query_for_invalid_date_range(self):
        actual_query = SubmissionDateRangeFilter('All Periods', ('+', 1, 30)).build_filter_query()
        self.assertEqual(actual_query, None)


class TestDateQuestionFilter(unittest.TestCase):
    def test_should_build_query_with_start_and_end_date_for_dd_mm_yy_format(self):
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='Some date question',
                                                                   date_format='dd.mm.yyyy')
        mock_form_model.id = 'form_id'

        actual_query = DateQuestionRangeFilter('21.11.2013-28.11.2013', mock_form_model, 'q1').build_filter_query()

        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'form_id_q1_value': {'gte': u'21.11.2013', 'lte': u'28.11.2013'}}})

    def test_should_build_query_with_start_and_end_date_for_mm_dd_yy_format(self):
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='Some date question',
                                                                   date_format='mm.dd.yyyy')
        mock_form_model.id = 'form_id'

        actual_query = DateQuestionRangeFilter('11.21.2013-11.28.2013', mock_form_model, 'q1').build_filter_query()

        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'form_id_q1_value': {'gte': u'11.21.2013', 'lte': u'11.28.2013'}}})


    def test_should_build_query_with_start_and_end_date_for_mm_yyyy_format(self):
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='q1',
                                                                   date_format='mm.yyyy')
        mock_form_model.id = 'form_id'
        actual_query = DateQuestionRangeFilter('11.2013-09.2013', mock_form_model, 'q1').build_filter_query()
        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'form_id_q1_value': {'gte': u'11.2013', 'lte': u'09.2013'}}})


    def test_should_call_query_match_for_current_day(self):
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code.return_value = DateField(name='q1', code='q1', label='q1',
                                                                   date_format='dd.mm.yyyy')
        mock_form_model.id = 'form_id'
        today = "26.11.2013"

        actual_query = DateQuestionRangeFilter(today, mock_form_model, 'q1').build_filter_query()

        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'form_id_q1_value': {'gte': u'26.11.2013', 'lte': u'26.11.2013'}}})

    def test_should_call_query_match_for_date_field_inside_fieldset(self):
        mock_form_model = MagicMock(spec=FormModel)
        mock_form_model.get_field_by_code_in_fieldset.return_value = DateField(name='q1', code='q1', label='q1',
                                                                               date_format='dd.mm.yyyy',
                                                                               parent_field_code='q1_parent')
        mock_form_model.id = 'form_id'
        today = "26.11.2013"

        actual_query = DateQuestionRangeFilter(today, mock_form_model, 'q1_parent:q1').build_filter_query()

        self.assertDictEqual(actual_query.to_dict(),
                             {'range': {'form_id_q1_parent-q1_value': {'gte': u'26.11.2013', 'lte': u'26.11.2013'}}})
