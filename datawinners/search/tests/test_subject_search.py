from unittest import TestCase
from django.http import HttpRequest
from elasticutils import S
from mock import patch, Mock
from datawinners.search.subject_search import search, replace_special_chars


class TestSubjectSearch(TestCase):
    def test_default_query_used_when_no_search_text(self):
        request = HttpRequest()
        request.POST['sSearch'] = ''
        request.POST['iDisplayStart'] = '0'
        request.POST['iDisplayLength'] = '10'
        request.POST['iSortCol_0'] = '1'
        request.user = 'teste'
        with patch("datawinners.search.subject_search.get_database_manager") as get_manager:
            with patch("datawinners.search.subject_search.header_fields") as header_fields:
                with patch("datawinners.search.subject_search.S") as search_object:
                    get_manager.return_value = Mock()
                    header_fields.return_value = {}
                    mock_search = Mock(spec=S)
                    mock_query = Mock()
                    mock_search.query.return_value = mock_query
                    mock_query.values_dict.return_value = {}
                    search_object.return_value = mock_search

                    search(request, 'st')

                    self.assertTrue(mock_search.query.called)
                    self.assertTrue(mock_query.count.called)
                    self.assertTrue(mock_search.count.called)

    def test_raw_query_used_when_for_search_text(self):
        request = HttpRequest()
        request.POST['sSearch'] = 'search string'
        request.POST['iDisplayStart'] = '0'
        request.POST['iDisplayLength'] = '10'
        request.POST['iSortCol_0'] = '1'
        request.user = 'teste'
        with patch("datawinners.search.subject_search.get_database_manager") as get_manager:
            with patch("datawinners.search.subject_search.header_fields") as header_fields:
                with patch("datawinners.search.subject_search.S") as search_object:
                    get_manager.return_value = Mock()
                    header_fields.return_value = {}
                    mock_search = Mock(spec=S)
                    mock_query = Mock()
                    mock_search.query.return_value = mock_query
                    mock_query_raw = Mock()
                    mock_search.query_raw.return_value = mock_query_raw
                    mock_query_raw.values_dict.return_value = {}

                    mock_query.values_dict.return_value = {}
                    search_object.return_value = mock_search

                    search(request, 'st')

                    self.assertTrue(mock_search.query.called)
                    mock_search.query_raw.assert_called_once_with(
                        {"query_string": {"fields": [], "query": "search string"}})
                    self.assertFalse(mock_query.count.called)
                    self.assertTrue(mock_query_raw.count.called)
                    self.assertTrue(mock_search.count.called)

    def test_replace_special_chars(self):
        text = 'sho\uld_change_+-!^(){}[]~*?:"should_not_change__e#$__change_this&&that||thus'
        result = replace_special_chars(text)
        expected = 'sho\\\\uld_change_\\+\\-\\!\\^\\(\\)\\{\\}\\[\\]\\~\\*\\?\\:\\"should_not_change__e#$__change_this\\&&that\\||thus'
        self.assertEquals(result, expected)
