import unittest
from pyelasticsearch import ElasticSearch
from mangrove.datastore.database import DatabaseManager
from mock import Mock, MagicMock
from datawinners.search.submission_index import SubmissionSearchStore
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, DateField
from mangrove.form_model.form_model import FormModel


class TestSubmissionSearchStore(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.default_ddtype = DataDictType(self.dbm, name='Default String Datadict Type', slug='string_default',
                                           primitive_type='string')
        fields = \
            [DateField(name='q3', code='q3', label='Reporting date', date_format='dd.mm.yyyy',
                       ddtype=Mock(spec=DataDictType)),
             TextField(name="Q1", code="EID", label="What is the reporting date?", entity_question_flag=True,
                       ddtype=self.default_ddtype)]
        self.form_model = FormModel(self.dbm, "abc", "abc", entity_type=["clinic"], form_code="cli001", fields=fields,
                                    type="survey")

    def test_should_add_es_mapping_when_no_existing_questions_mapping(self):
        dbm = MagicMock(spec=DatabaseManager)
        dbm.database_name = 'somedb'
        es = Mock()
        no_old_mapping = []
        es.get_mapping.return_value = no_old_mapping

        SubmissionSearchStore(dbm, es, self.form_model).update_store()

        self.assertTrue(es.put_mapping.called)
