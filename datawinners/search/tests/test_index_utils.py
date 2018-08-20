import unittest

from mock import Mock, patch

from datawinners.search.index_utils import subject_dict
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.form_model import EntityFormModel
from mangrove.form_model.field import TextField


class TestIndexUtils(unittest.TestCase):

    def test_subject_index_dict(self):
        dbm = Mock(spec=DatabaseManager)
        entity_type = ['entity_type']

        mock_entity = Entity(dbm=dbm, entity_type=entity_type)
        mock_entity.add_data(data=[('name1', 'ans1'), ('name2', 'ans2')])

        with patch.object(Entity, 'get') as get:
            get.return_value = mock_entity
            form_model = EntityFormModel(dbm=dbm, entity_type=entity_type)
            form_model.add_field(TextField('name1', 'code1', 'label1'))
            form_model.add_field(TextField('name2', 'code2', 'label2'))
            form_model._doc = Mock(form_code="abc", id='form_id')
            entity_doc = Mock()

            result = subject_dict(entity_type, entity_doc, dbm, form_model)

            expected = {'form_id_code1': 'ans1', 'form_id_code2': 'ans2', 'entity_type': ['entity_type'],
                        'void': False}
            self.assertEquals(result, expected)
