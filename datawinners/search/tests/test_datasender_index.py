import unittest
from mock import Mock, patch
from datawinners.search.datasender_index import _update_datasender_index
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import FormModel


class TestDatasenderIndex(unittest.TestCase):
    def test_should_not_create_index_for_testdatasenders(self):
        dbm = Mock(spec=DatabaseManager)
        entity_doc = Entity(dbm, entity_type='reporter', short_code='test')

        with patch("datawinners.search.datasender_index.elasticutils.get_es") as es:
            es.return_value = Mock
            _update_datasender_index(entity_doc, dbm)
            self.assertFalse(es.index.call_count)

    def test_should_create_index_for_datasenders(self):
        dbm = Mock(spec=DatabaseManager)
        dbm.database_name = 'db'
        entity_doc = Mock(spec=Entity)
        entity_doc.data.return_value = {"name": "test_name", "mobile": "344455"}
        entity_doc.id = 'some_id'
        entity_doc.aggregation_paths = {"_type": ["reporter"]}

        with patch("datawinners.search.datasender_index.elasticutils.get_es") as es:
            with patch("datawinners.search.datasender_index.get_form_model_by_code") as get_form_model:
                with patch("datawinners.search.datasender_index._create_datasender_dict") as create_ds_dict:
                    mock_form_model = Mock(spec=FormModel)
                    mock_ds_dict = {"name": "name"}
                    get_form_model.return_value = mock_form_model
                    create_ds_dict.return_value = mock_ds_dict
                    mock_es = Mock()
                    es.return_value = mock_es

                    _update_datasender_index(entity_doc, dbm)

                    mock_es.index.assert_called_with('db','reporter', mock_ds_dict,id='some_id')
