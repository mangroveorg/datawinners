import unittest
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from mock import Mock, patch
from questionnaire.questionnaire_builder import QuestionnaireBuilder

class TestQuestionnaireBuilder(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.ddtype = Mock(spec=DataDictType)

        self.patcher = patch("questionnaire.questionnaire_builder.get_datadict_type_by_slug")
        self.get_datadict_type_by_slug_mock = self.patcher.start()
        self.get_datadict_type_by_slug_mock.return_value = self.ddtype


    def tearDown(self):
        self.patcher.stop()


    def test_should_update_questionnaire_when_entity_type_is_not_reporter(self):
        form_model = FormModel(self.dbm, name="test", label="test", form_code="fc",
            fields=[Mock(spec=TextField), Mock(spec=TextField)],
            entity_type=["clinic"], type="survey")

        post = [{"title": "What is your age", "code": "age", "type": "integer", "choices": [],
                "is_entity_question": False,
                "range_min": 0, "range_max": 100}]

        QuestionnaireBuilder(form_model,self.dbm).update_questionnaire_with_questions(post)
        self.assertEquals(1, len(form_model.fields))


    def test_should_update_questionnaire_when_entity_type_is_reporter(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": False,
                 "min_length": 1, "max_length": ""},
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        form_model = FormModel(self.dbm, "act_rep", "act_rep", "test", [], ["reporter"], "test")
        QuestionnaireBuilder(form_model,self.dbm).update_questionnaire_with_questions(post)
        self.assertEqual(4, len(form_model.fields))
        entity_id_question = form_model.entity_question
        self.assertEqual('eid', entity_id_question.code)
        self.assertEqual('I am submitting this data on behalf of', entity_id_question.name)
        self.assertEqual("Choose Data Sender from this list.", entity_id_question.instruction)

    def test_should_save_questionnaire_from_post(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 "min_length": 1, "max_length": ""},
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        form_model = FormModel(self.dbm, "test", "test", "test", [Mock(spec=TextField)], ["test"], "test")
        QuestionnaireBuilder(form_model,self.dbm).update_questionnaire_with_questions(post)
        self.assertEqual(3, len(form_model.fields))
