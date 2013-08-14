from unittest import TestCase
import elasticutils
from mock import patch, Mock
from datawinners.search.subject_search import paginated_search, replace_special_chars, entity_dict
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import FormModel


class TestSubjectSearch(TestCase):
    def test_default_query_used_when_no_search_text(self):
        search_params = {}
        search_params.update({'search_text': ''})
        search_params.update({'start_result_number': '0'})
        search_params.update({'number_of_results': '10'})
        search_params.update({'order': ''})
        search_params.update({'order_by': 1})
        with patch("datawinners.search.subject_search.get_database_manager") as get_manager:
            with patch("datawinners.search.subject_search.header_fields") as header_fields:
                with patch("datawinners.search.subject_search.S") as search_object:
                    get_manager.return_value = Mock()
                    header_values = {'name': 'Name', 'place': 'Place'}
                    header_fields.return_value = header_values

                    mock_search = Mock()
                    query = Mock()
                    query.values_dict = Mock(return_value=[])
                    search_obj = Mock(spec=elasticutils.S)
                    mock_search.order_by.return_value = search_obj

                    filtered_search_obj = Mock(spec=elasticutils.S)
                    search_obj.filter.return_value = filtered_search_obj

                    filtered_search_obj.query.return_value = query
                    search_object.return_value = mock_search

                    paginated_search("test", 'st', search_params)

                    self.assertTrue(filtered_search_obj.query.called)
                    self.assertTrue(filtered_search_obj.count.called)
                    search_obj.filter.assert_called_once_with(void=False)
                    self.assertTrue(query.count.called)

    def test_raw_query_used_when_for_search_text(self):
        search_params = {}
        search_params.update({'search_text': 'search string'})
        search_params.update({'start_result_number': '0'})
        search_params.update({'number_of_results': '10'})
        search_params.update({'order': ''})
        search_params.update({'order_by': 1})
        with patch("datawinners.search.subject_search.get_database_manager") as get_manager:
            with patch("datawinners.search.subject_search.header_fields") as header_fields:
                with patch("datawinners.search.subject_search.S") as search_object:
                    get_manager.return_value = Mock()
                    header_values = {'name': 'Name', 'place': 'Place'}
                    header_fields.return_value = header_values

                    mock_search = Mock()
                    query = Mock()
                    query.values_dict = Mock(return_value=[])
                    search_obj = Mock(spec=elasticutils.S)
                    mock_search.order_by.return_value = search_obj

                    filtered_search_obj = Mock(spec=elasticutils.S)
                    search_obj.filter.return_value = filtered_search_obj

                    filtered_search_obj.query_raw.return_value = query
                    search_object.return_value = mock_search

                    paginated_search("test", 'st', search_params)

                    self.assertTrue(filtered_search_obj.query_raw.called)
                    filtered_search_obj.query_raw.assert_called_once_with(
                        {"query_string": {"fields": ['place', 'name'], "query": "search string"}})
                    self.assertTrue(query.count.called)
                    self.assertTrue(filtered_search_obj.count.called)
                    search_obj.filter.assert_called_once_with(void=False)

    def test_replace_special_chars(self):
        text = 'sho\uld_change_+-!^(){}[]~*?:"should_not_change__e#$__change_this&&that||thus'
        result = replace_special_chars(text)
        expected = 'sho\\\\uld_change_\\+\\-\\!\\^\\(\\)\\{\\}\\[\\]\\~\\*\\?\\:\\"should_not_change__e#$__change_this\\&&that\\||thus'
        self.assertEquals(result, expected)


    def test_created_subject_index_documents_should_have_void_field(self):
        with patch("datawinners.search.subject_search.get_entity_type_fields") as get_entity_type_fields:
            with patch(
                    "datawinners.search.subject_search.get_form_model_by_entity_type") as get_form_model_by_entity_type:
                with patch("datawinners.search.subject_search._tabulate_data") as _tabulate_data:
                    with patch("datawinners.search.subject_search.Entity.get") as entity_get:
                        mock_subject = Mock(spec=Entity)
                        entity_get.return_value = mock_subject
                        _tabulate_data.return_value = {"cols": [{"q1": 'ans1'}]}
                        get_form_model_by_entity_type.return_value = Mock(spec=FormModel)
                        get_entity_type_fields.return_value = ['field1'], ['label1'], ['q1']
                        mock_subject.is_void.return_value = False

                        moc_entity_doc = Mock()
                        moc_entity_doc.id.return_value = 1
                        result = entity_dict("some_subject", moc_entity_doc, Mock(spec=DatabaseManager))

                        self.assertEquals(result["void"], False)
                        self.assertEquals(result["entity_type"], "some_subject")


