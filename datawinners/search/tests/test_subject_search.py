from unittest import TestCase
from django.http import HttpRequest
import elasticutils
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
                    header_values = {'name': 'Name', 'place': 'Place'}
                    header_fields.return_value = header_values

                    mock_search = Mock()
                    query = Mock()
                    query.values_dict = Mock(return_value=[])
                    order_by = Mock(spec=elasticutils.S)
                    mock_search.order_by.return_value = order_by
                    order_by.query.return_value = query
                    search_object.return_value = mock_search

                    search(request, 'st')

                    self.assertTrue(order_by.query.called)
                    self.assertTrue(order_by.count.called)
                    self.assertTrue(query.count.called)

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
                    header_fields.return_value = {'name': 'Name', 'place': 'Place'}
                    mock_search = Mock()
                    query = Mock()
                    query.values_dict = Mock(return_value=[])
                    order_by = Mock(spec=elasticutils.S)
                    mock_search.order_by.return_value = order_by
                    order_by.query_raw.return_value = query
                    search_object.return_value = mock_search

                    search(request, 'st')

                    self.assertTrue(order_by.query_raw.called)
                    order_by.query_raw.assert_called_once_with(
                        {"query_string": {"fields": ['place','name'], "query": "search string"}})
                    self.assertTrue(query.count.called)
                    self.assertTrue(order_by.count.called)

    def test_replace_special_chars(self):
        text = 'sho\uld_change_+-!^(){}[]~*?:"should_not_change__e#$__change_this&&that||thus'
        result = replace_special_chars(text)
        expected = 'sho\\\\uld_change_\\+\\-\\!\\^\\(\\)\\{\\}\\[\\]\\~\\*\\?\\:\\"should_not_change__e#$__change_this\\&&that\\||thus'
        self.assertEquals(result, expected)
