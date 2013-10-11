import unittest
from mock import Mock, patch, PropertyMock
from datawinners.search.datasender_index import update_datasender_index, _get_project_names_by_datasender_id
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import FormModel


class TestDatasenderIndex(unittest.TestCase):
    def test_should_not_create_index_for_testdatasenders(self):
        dbm = Mock(spec=DatabaseManager)
        entity_doc = Entity(dbm, entity_type='reporter', short_code='test')

        with patch("datawinners.search.datasender_index.elasticutils.get_es") as es:
            es.return_value = Mock
            update_datasender_index(entity_doc, dbm)
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

                    update_datasender_index(entity_doc, dbm)

                    mock_es.index.assert_called_with('db', 'reporter', mock_ds_dict, id='some_id')

    def test_project_names_should_be_in_alphabetical_order(self):
        dbm = Mock(spec=DatabaseManager)
        entity_id = "rep"
        project1 = Mock()
        type(project1).value = PropertyMock(return_value={"name": "nameA", "value": "value1"})
        project2 = Mock()
        type(project2).value = PropertyMock(return_value={"name": "nameB", "value": "value2"})

        with patch("datawinners.search.datasender_index.get_all_projects") as get_all_projects:
            get_all_projects.return_value = [project2, project1]
            result = _get_project_names_by_datasender_id(dbm, entity_id)

            self.assertEquals(["nameA", "nameB"], result)

