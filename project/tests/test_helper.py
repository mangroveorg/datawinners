# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from datawinners.project import helper
from mangrove.datastore.database import get_db_manager
from mangrove.form_model.field import TextField, IntegerField, SelectField
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import IntegerConstraint


class TestHelper(unittest.TestCase):
    def test_creates_questions_from_dict(self):
        post = [{"title": "q1", "code": "qc1", "description": "desc1", "type": "text", "choices": [],
                 "is_entity_question": True, "min_length": 1, "max_length": 15},
                {"title": "q2", "code": "qc2", "description": "desc2", "type": "integer", "choices": [],
                 "is_entity_question": False, "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "description": "desc3", "type": "select",
                 "choices": [{"value": "c1"}, {"value": "c2"}], "is_entity_question": False,
                 "answers_permitted": "single"}
        ]
        q1 = helper.create_question(post[0])
        q2 = helper.create_question(post[1])
        q3 = helper.create_question(post[2])
        self.assertIsInstance(q1, TextField)
        self.assertIsInstance(q2, IntegerField)
        self.assertIsInstance(q3, SelectField)
        self.assertEquals(q2._to_json()["range"], {"min": 0, "max": 100})
        self.assertEquals(q1._to_json()["length"], {"min": 1, "max": 15})

    def test_should_save_questionnaire_from_post(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 "min_length": 1, "max_length": ""},
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False, "answers_permitted": "single"}
        ]
        q1 = helper.create_question(post[0])
        form_model = FormModel(get_db_manager(), "test", "test", "test", [q1], "test", "test")
        questionnaire = helper.update_questionnaire_with_questions(form_model, post)
        self.assertEqual(3, len(questionnaire.fields))

    def test_should_create_integer_question_with_no_max_constraint(self):
        post = [{"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": ""}]
        q1 = helper.create_question(post[0])
        self.assertEqual(q1.constraint.max, None)

    def test_should_return_code_title_tuple_list(self):
        question1 = TextField(label="entity_question", question_code="ID", name="What is associated entity"
                              , language="eng", entity_question_flag=True)
        question2 = TextField(label="question1_Name", question_code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng")
        self.assertEquals([("ID", "What is associated entity"), ("Q1", "What is your name")], helper.get_code_and_title([question1, question2]))

    def test_should_create_text_question_with_no_max_length(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 "min_length": 1, "max_length": ""},
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False, "answers_permitted": "single"}
        ]
        q1 = helper.create_question(post[0])
        self.assertEqual(q1.constraint.max, None)

    def test_should_create_text_question_with_no_max_lengt_and_min_length(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 },
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False, "answers_permitted": "single"}
        ]
        q1 = helper.create_question(post[0])
        self.assertEqual(q1.constraint.max, None)
        self.assertEqual(q1.constraint.min, None)

    def test_should_return_code_title_tuple_list(self):
        question1 = TextField(label="entity_question", question_code="ID", name="What is associated entity"
                              , language="eng", entity_question_flag=True)
        question2 = TextField(label="question1_Name", question_code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng")
        self.assertEquals([("ID", "What is associated entity"), ("Q1", "What is your name")], helper.get_code_and_title([question1, question2]))
