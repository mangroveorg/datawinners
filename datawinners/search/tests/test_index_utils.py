import unittest

from mock import Mock, patch

from datawinners.search.index_utils import subject_dict
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import EntityFormModel


class TestIndexUtils(unittest.TestCase):
    def test_subject_index_dict(self):
        dbm = Mock(spec=DatabaseManager)
        entity_type = ['entity_type']

        with patch('datawinners.search.index_utils.get_entity_type_fields') as get_entity_type:
            with patch('datawinners.search.index_utils.tabulate_data') as tabulate_data:
                get_entity_type.return_value = ['name1', 'name2'], ['label1', 'label2'], ['code1', 'code2']
                mock_entity = Mock(spec=Entity)
                mock_entity.is_void.return_value = False
                tabulate_data.return_value = {'cols': ['ans1', 'ans2']}
                with patch.object(Entity, 'get') as get:
                    get.return_value = mock_entity
                    form_model = EntityFormModel(dbm=dbm, entity_type=entity_type)
                    form_model._doc = Mock(form_code="abc", id='form_id')
                    entity_doc = Mock()

                    result = subject_dict(entity_type, entity_doc, dbm, form_model)

                    expected = {'form_id_code1': 'ans1', 'form_id_code2': 'ans2', 'entity_type': ['entity_type'],
                                'void': False}
                    self.assertEquals(result, expected)
