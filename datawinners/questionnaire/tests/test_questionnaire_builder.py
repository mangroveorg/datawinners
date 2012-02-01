import unittest
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, IntegerField, SelectField, HierarchyField, GeoCodeField, TelephoneNumberField
from mangrove.form_model.form_model import FormModel, LOCATION_TYPE_FIELD_NAME
from mock import Mock, patch
from questionnaire.questionnaire_builder import QuestionnaireBuilder, QuestionBuilder

class TestQuestionnaireBuilder(unittest.TestCase):

    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.patcher = _patch_get_ddtype_by_slug()


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


class TestQuestionBuilder(unittest.TestCase):

    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.patcher = _patch_get_ddtype_by_slug()
        self.question_builder = QuestionBuilder(self.dbm)

    def tearDown(self):
        self.patcher.stop()

    def test_creates_questions_from_dict(self):
        post = [{"title": "q1", "code": "qc1", "description": "desc1", "type": "text", "choices": [],
                 "is_entity_question": True, "min_length": 1, "max_length": 15},
                {"title": "q2", "code": "qc2", "description": "desc2", "type": "integer", "choices": [],
                 "is_entity_question": False, "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "description": "desc3", "type": "select",
                 "choices": [{"value": "c1"}, {"value": "c2"}], "is_entity_question": False},
                {"title": "q4", "code": "qc4", "description": "desc4", "type": "select1",
                 "choices": [{"value": "c1"}, {"value": "c2"}], "is_entity_question": False},
                {"title": "q5", "code": "qc5", "description": "desc4", "type": "text"}
        ]
        language = 'en'
        q1 = self.question_builder.create_question(post[0], language)
        q2 = self.question_builder.create_question(post[1], language)
        q3 = self.question_builder.create_question(post[2], language)
        q4 = self.question_builder.create_question(post[3], language)
        q5 = self.question_builder.create_question(post[4], language)
        self.assertIsInstance(q1, TextField)
        self.assertIsInstance(q2, IntegerField)
        self.assertIsInstance(q3, SelectField)
        self.assertIsInstance(q4, SelectField)
        self.assertIsInstance(q5, TextField)
        self.assertEquals(q1._to_json_view()["length"], {"min": 1, "max": 15})
        self.assertEquals(q2._to_json_view()["range"], {"min": 0, "max": 100})
        self.assertEquals(q3._to_json_view()["type"], "select")
        self.assertEquals(q4._to_json_view()["type"], "select1")
        self.assertEquals(q5._to_json_view()["type"], "text")

    def test_should_populate_name_as_title_if_name_is_not_present(self):
        post = {"title": "q2", "code": "qc2", "type": "text"}
        q1 = self.question_builder.create_question(post,'en')
        self.assertEqual('q2',q1.name)

    def test_should_honour_name(self):
        post = {"name": "name", "title":'q2',"code": "qc2", "type": "text"}
        q1 = self.question_builder.create_question(post,'en')
        self.assertEqual('name',q1.name)

    def test_should_create_integer_question_with_no_max_constraint(self):
        post = [{"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": ""}]
        q1 = self.question_builder.create_question(post[0],'en')
        self.assertEqual(None,q1.constraints[0].max)
        self.assertEqual(0,q1.constraints[0].min)

    def test_should_create_geo_code_question(self):
        CODE = "lc3"
        LABEL = "what is your location"
        TYPE = "geocode"
        post = {"title": LABEL, "code": CODE, "type": TYPE}

        geo_code_field = self.question_builder.create_question(post,'en')

        self.assertIsInstance(geo_code_field, GeoCodeField)
        self.assertEqual(CODE, geo_code_field.code)

    def test_should_create_select1_question(self):
        CODE = "qc3"
        LABEL = "q3"
        TYPE = "select1"
        choices = [{"text":"first","val": "c1"}, {"text":"second","val": "c2"}]

        post = {"title": LABEL, "code": CODE, "type": TYPE, "choices": choices}

        select1_question = self.question_builder.create_question(post, 'en')

        self.assertEqual(LABEL, select1_question.label['en'])
        self.assertEqual(2, len(select1_question.options))
        self.assertEqual("c1", select1_question.options[0]['val'])
        self.assertEqual("c2", select1_question.options[1]['val'])

    def test_should_create_select_question(self):
        CODE = "qc3"
        LABEL = "q3"
        TYPE = "select"
        choices = [{"text":"first","val": "c1"}, {"text":"second","val": "c2"}]

        post = {"title": LABEL, "code": CODE, "type": TYPE, "choices": choices}

        select_question = self.question_builder.create_question(post, 'en')

        self.assertEqual(LABEL, select_question.label['en'])
        self.assertEqual(2, len(select_question.options))
        self.assertEqual("c1", select_question.options[0]['val'])
        self.assertEqual("c2", select_question.options[1]['val'])

    def test_should_create_date_question(self):
        CODE = "qc3"
        LABEL = "q3"
        TYPE = "date"

        date_format = "dd.mm.yyyy"
        post = {"title": LABEL, "code": CODE, "type": TYPE, "date_format": date_format}

        date_question = self.question_builder.create_question(post, 'en')

        self.assertEqual(LABEL, date_question.label['en'])
        self.assertEqual(date_format, date_question.date_format)

    def test_should_create_text_question_with_no_max_length_and_min_length(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 },
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        q1 = self.question_builder.create_question(post[0], 'en')
        self.assertEqual(q1.constraints, [])
        self.assertEqual(q1.label['en'], 'q1')

    def test_should_create_text_question_for_french_language(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 },
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        language = 'fr'
        q1 = self.question_builder.create_question(post[0],language=language)
        self.assertEqual(q1.constraints, [])
        self.assertEqual(q1.label[language], 'q1')


    def test_should_create_telephone_number_question(self):
        CODE = "qc3"
        LABEL = "q3"
        TYPE = "telephone_number"

        post = {"title": LABEL, "code": CODE, "type": TYPE}

        select_question = self.question_builder.create_question(post, 'en')

        self.assertIsInstance(select_question,TelephoneNumberField)

    def test_should_create_location_question(self):
        CODE = "qc3"
        LABEL = "q3"
        TYPE = "list"

        post = {"title": LABEL, "code": CODE, "type": TYPE }

        select_question = self.question_builder.create_question(post, 'en')
        self.assertEqual(LOCATION_TYPE_FIELD_NAME,select_question.name)



def _patch_get_ddtype_by_slug():
    patcher = patch("questionnaire.questionnaire_builder.get_datadict_type_by_slug")
    get_datadict_type_by_slug_mock = patcher.start()
    get_datadict_type_by_slug_mock.return_value = Mock(spec=DataDictType)
    return patcher
