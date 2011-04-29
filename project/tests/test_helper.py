# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from django.db import database
from datawinners.project import helper
#from mangrove.datastore.question import TextQuestion
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.field import TextField, SelectField, IntegerField
from mangrove.form_model.form_model import FormModel

class TestHelper(unittest.TestCase):

    def test_creates_questions_from_dict(self):
        post = [{ "title":"q1", "code":"qc1", "description":"desc1", "type":"text", "choices":[] , "is_entity_question":True},
                { "title":"q2", "code":"qc2", "description":"desc2", "type":"integer", "choices":[], "is_entity_question":False},
                { "title":"q3", "code":"qc3", "description":"desc3", "type":"choice", "choices":[{ "value":"c1" }, { "value":"c2" } ], "is_entity_question":False}
               ]
        q1=helper.create_question(post[0])
        q2=helper.create_question(post[1])
        q3=helper.create_question(post[2])
        self.assertIsInstance(q1,TextField)
        self.assertIsInstance(q2,IntegerField)
        self.assertIsInstance(q3,SelectField)

    def test_should_save_questionnaire_from_post(self):
        post = [{ "title":"q1", "code":"qc1", "description":"desc1", "type":"text", "choices":[], "is_entity_question":True},
                { "title":"q2", "code":"qc2", "description":"desc2", "type":"integer", "choices":[], "is_entity_question":False },
                { "title":"q3", "code":"qc3", "description":"desc3", "type":"choice", "choices":[{ "value":"c1" }, { "value":"c2" } ], "is_entity_question":False}
               ]
        q1=helper.create_question(post[0])
        form_model=FormModel(get_db_manager(),"test","test","test",[q1],"test","test")
        questionnaire = helper.save_questionnaire(form_model,post)
        self.assertEqual(3,len(questionnaire.fields))

