import unittest
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from datawinners.project.wizard_view import _get_deleted_question_codes


class TestWizardView(unittest.TestCase):
    def test_should_give_deleted_question_codes(self):
        changed_question = {'added':['question1'],'deleted':['question2','question3']}
        field1 = TextField(name='name1',code='q1',label='question1',ddtype=Mock(spec=DataDictType))
        field2 = TextField(name='name2',code='q2',label='question2',ddtype=Mock(spec=DataDictType))
        field3 = TextField(name='name3',code='q3',label='question3',ddtype=Mock(spec=DataDictType))
        form_model = FormModel(dbm=Mock(spec=DatabaseManager),name='form_model',fields=[field1,field2,field3])
        result = _get_deleted_question_codes(changed_question, form_model)
        self.assertEqual(result,['q2','q3'])