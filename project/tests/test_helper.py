# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime

import unittest
from mock import Mock, patch
from datawinners.project import helper
from datawinners.project.models import Project
from mangrove.datastore.database import  DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel
from mangrove.datastore import data
from copy import copy
from mangrove.datastore.aggregrate import Sum, Latest
from mangrove.form_model.validation import TextConstraint, NumericConstraint


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch("datawinners.project.helper.create_datadict_type")
        self.patcher2 = patch("datawinners.project.helper.get_datadict_type_by_slug")
        self.create_ddtype_mock = self.patcher1.start()
        self.get_datadict_type_by_slug_mock = self.patcher2.start()
        self.create_ddtype_mock.return_value = Mock(spec=DataDictType)
        self.get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
        self.dbm = Mock(spec=DatabaseManager)


    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_creates_questions_from_dict(self):
        post = [{"title": "q1", "code": "qc1", "description": "desc1", "type": "text", "choices": [],
                 "is_entity_question": True, "min_length": 1, "max_length": 15},
                {"title": "q2", "code": "qc2", "description": "desc2", "type": "integer", "choices": [],
                 "is_entity_question": False, "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "description": "desc3", "type": "select",
                 "choices": [{"value": "c1"}, {"value": "c2"}], "is_entity_question": False},
                {"title": "q4", "code": "qc4", "description": "desc4", "type": "select1",
                 "choices": [{"value": "c1"}, {"value": "c2"}], "is_entity_question": False}
        ]
        q1 = helper.create_question(post[0], self.dbm)
        q2 = helper.create_question(post[1], self.dbm)
        q3 = helper.create_question(post[2], self.dbm)
        q4 = helper.create_question(post[3], self.dbm)
        self.assertIsInstance(q1, TextField)
        self.assertIsInstance(q2, IntegerField)
        self.assertIsInstance(q3, SelectField)
        self.assertIsInstance(q4, SelectField)
        self.assertEquals(q1._to_json_view()["length"], {"min": 1, "max": 15})
        self.assertEquals(q2._to_json_view()["range"], {"min": 0, "max": 100})
        self.assertEquals(q3._to_json_view()["type"], "select")
        self.assertEquals(q4._to_json_view()["type"], "select1")

    def test_should_save_questionnaire_from_post(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 "min_length": 1, "max_length": ""},
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        q1 = helper.create_question(post[0], self.dbm)
        form_model = FormModel(self.dbm, "test", "test", "test", [q1], ["test"], "test")
        questionnaire = helper.update_questionnaire_with_questions(form_model, post, self.dbm)
        self.assertEqual(3, len(questionnaire.fields))

    def test_should_create_integer_question_with_no_max_constraint(self):
        post = [{"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": ""}]
        q1 = helper.create_question(post[0], self.dbm)
        self.assertEqual(q1.constraint.max, None)

    def test_should_return_code_title_tuple_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="entity_question", code="ID", name="What is associated entity",
                              language="eng", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        self.assertEquals([("ID", "What is associated entity"), ("Q1", "What is your name")],
                                                                                            helper.get_code_and_title(
                                                                                                [question1, question2]))

    def test_should_create_text_question_with_no_max_length(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 "min_length": 1, "max_length": ""},
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        q1 = helper.create_question(post[0], self.dbm)
        self.assertEqual(q1.constraint.max, None)

    def test_should_create_text_question_with_no_max_lengt_and_min_length(self):
        post = [{"title": "q1", "code": "qc1", "type": "text", "choices": [], "is_entity_question": True,
                 },
                {"title": "q2", "code": "qc2", "type": "integer", "choices": [], "is_entity_question": False,
                 "range_min": 0, "range_max": 100},
                {"title": "q3", "code": "qc3", "type": "select", "choices": [{"value": "c1"}, {"value": "c2"}],
                 "is_entity_question": False}
        ]
        q1 = helper.create_question(post[0], self.dbm)
        self.assertEqual(q1.constraint.max, None)
        self.assertEqual(q1.constraint.min, None)

    def test_should_return_tuple_list_of_submissions(self):
        questions = [("Q1", "Question 1"), ("Q2", "Question 2")]
        submissions = [
                {'values': {'q1': 'ans1', 'q2': 'ans2'}, 'channel': 'sms', 'status': True, 'voided': False, 'test':False,
                 'created': datetime(2011, 1, 1), 'error_message': 'error1', 'destination': '2616', 'source': '1234'},
                {'values': {'q2': 'ans22'}, 'channel': 'sms', 'status': False, 'voided': True, 'test':True,
                 'created': datetime(2011, 1, 2),
                 'error_message': 'error2', 'destination': '2616', 'source': '1234'}
        ]
        required_submissions = [('2616', '1234', datetime(2011, 1, 1), True, False, 'error1', 'ans1', 'ans2',),
                ('2616', helper.TEST_FLAG, datetime(2011, 1, 2), False, True, 'error2', None, 'ans22',),
                                                                                                              ]
        self.assertEquals(required_submissions, helper.get_submissions(questions, submissions))

    def test_should_create_text_question_with_implicit_ddtype(self):
        post = {"title": "what is your name", "code": "qc1", "description": "desc1", "type": "text",
                "choices": [],
                "is_entity_question": True, "min_length": 1, "max_length": 15}

        dbm = Mock(spec=DatabaseManager)

        self.create_ddtype_mock.return_value = DataDictType(dbm, "qc1", "what_is_your_name", "text",
                                                            "what is your name")

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            text_question = helper.create_question(post, dbm)

        self.create_ddtype_mock.assert_called_once_with(dbm=dbm, name="qc1", slug="what_is_your_name",
                                                        primitive_type="text", description="what is your name")
        self.assertEqual('qc1', text_question.ddtype.name)
        self.assertEqual("what is your name", text_question.ddtype.description)
        self.assertEqual("what_is_your_name", text_question.ddtype.slug)
        self.assertEqual("text", text_question.ddtype.primitive_type)

    def test_should_create_integer_question_with_implicit_ddtype(self):
        post = {"title": "What is your age", "code": "age", "type": "integer", "choices": [],
                "is_entity_question": False,
                "range_min": 0, "range_max": 100}

        dbm = Mock(spec=DatabaseManager)

        self.create_ddtype_mock.return_value = DataDictType(dbm, "age", "what_is_your_age", "integer",
                                                            "what is your age")

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            integer_question = helper.create_question(post, dbm)

        self.create_ddtype_mock.assert_called_once_with(dbm=dbm, name="age", slug="what_is_your_age",
                                                        primitive_type="integer", description="What is your age")
        self.assertEqual('age', integer_question.ddtype.name)
        self.assertEqual("what is your age", integer_question.ddtype.description)
        self.assertEqual("what_is_your_age", integer_question.ddtype.slug)
        self.assertEqual("integer", integer_question.ddtype.primitive_type)

    def test_should_create_select_question_with_implicit_ddtype(self):
        CODE = "qc3"
        LABEL = "q3"
        SLUG = "q3"
        TYPE = "select"
        post = {"title": LABEL, "code": CODE, "type": TYPE, "choices": [{"value": "c1"}, {"value": "c2"}],
                "is_entity_question": False}

        dbm = Mock(spec=DatabaseManager)

        expected_data_dict = DataDictType(dbm, CODE, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            integer_question = helper.create_question(post, dbm)

        self.create_ddtype_mock.assert_called_once_with(dbm=dbm, name=CODE, slug=SLUG,
                                                        primitive_type=TYPE, description=LABEL)
        self.assertEqual(expected_data_dict, integer_question.ddtype)

    def test_should_create_select1_question_with_implicit_ddtype(self):
        CODE = "qc3"
        LABEL = "q3"
        SLUG = "q3"
        TYPE = "select1"
        post = {"title": LABEL, "code": CODE, "type": TYPE, "choices": [{"value": "c1"}, {"value": "c2"}],
                "is_entity_question": False}

        dbm = Mock(spec=DatabaseManager)

        expected_data_dict = DataDictType(dbm, CODE, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            integer_question = helper.create_question(post, dbm)

        self.create_ddtype_mock.assert_called_once_with(dbm=dbm, name=CODE, slug=SLUG,
                                                        primitive_type=TYPE, description=LABEL)
        self.assertEqual(expected_data_dict, integer_question.ddtype)

    def test_should_create_date_question_with_implicit_ddtype(self):
        CODE = "qc3"
        LABEL = "q3"
        SLUG = "q3"
        TYPE = "date"
        post = {"title": LABEL, "code": CODE, "type": TYPE, "date_format": "%m.%Y",
                "is_entity_question": False}

        dbm = Mock(spec=DatabaseManager)

        expected_data_dict = DataDictType(dbm, CODE, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            integer_question = helper.create_question(post, dbm)

        self.create_ddtype_mock.assert_called_once_with(dbm=dbm, name=CODE, slug=SLUG,
                                                        primitive_type=TYPE, description=LABEL)
        self.assertEqual(expected_data_dict, integer_question.ddtype)

    def test_should_create_questionnaire_with_entity_question(self):
        NAME = "eid"
        LABEL = "Entity ID"
        SLUG = "entity_id"
        TYPE = "string"
        post = {"entity_type": "Water Point", "name": "Test Project"}
        dbm = Mock(spec=DatabaseManager)

        patcher = patch("datawinners.project.helper.generate_questionnaire_code")
        mock = patcher.start()
        mock.return_value = '001'

        expected_data_dict = DataDictType(dbm, NAME, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            form_model = helper.create_questionnaire(post, dbm)

        self.create_ddtype_mock.assert_called_twice_with(dbm=dbm, name=NAME, slug=SLUG,
                                                         primitive_type=TYPE, description=LABEL)
        self.assertEqual(expected_data_dict, form_model.fields[0].ddtype)

        self.assertEqual(1, len(form_model.fields))
        self.assertEqual(True, form_model.fields[0].is_entity_field)
        self.assertEqual(["Water Point"], form_model.entity_type)
        self.assertFalse(form_model.is_active())
        patcher.stop()

    def test_should_update_questionnaire(self):
        dbm = Mock(spec=DatabaseManager)
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="name", code="na", name="What is your name",
                              language="eng", ddtype=ddtype)
        question2 = TextField(label="address", code="add", name="What is your address",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        post = {"title": "What is your age", "code": "age", "type": "integer", "choices": [],
                "is_entity_question": False,
                "range_min": 0, "range_max": 100}
        form_model = FormModel(dbm, name="test", label="test", form_code="fc", fields=[question1, question2],
                               entity_type=["reporter"], type="survey")
        form_model2 = helper.update_questionnaire_with_questions(form_model, [post], dbm)
        self.assertEquals(2, len(form_model2.fields))

    def test_should_generate_unique_questionnaire_code(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()
        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()
        dbm = Mock(spec=DatabaseManager)

        form_code_mock.side_effect = FormModelDoesNotExistsException('')
        models_mock.get_all_projects.return_value = []
        self.assertEqual(helper.generate_questionnaire_code(dbm), "001")

        myproject = Mock(spec=Project)
        models_mock.get_all_projects.return_value = [myproject]
        self.assertEqual(helper.generate_questionnaire_code(dbm), "002")

        patcher.stop()
        patcher1.stop()

    def test_should_generate_next_questionnaire_code_if_code_already_exists(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()

        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()

        dbm = Mock(spec=DatabaseManager)

        myproject = Mock(spec=Project)
        models_mock.get_all_projects.return_value = [myproject]

        def expected_side_effect(*args, **kwargs):
            code = kwargs.get('code') or args[1]
            if code == "003":
                raise FormModelDoesNotExistsException('')
            if code == "002":
                return Mock(spec=FormModel)

        form_code_mock.side_effect = expected_side_effect

        self.assertEqual(helper.generate_questionnaire_code(dbm), "003")

        patcher.stop()
        patcher1.stop()

    def test_should_create_location_question_with_implicit_ddtype(self):
        CODE = "lc3"
        LABEL = "what is your location"
        SLUG = "what_is_your_location"
        TYPE = "geocode"
        post = {"title": LABEL, "code": CODE, "type": TYPE, "is_entity_question": False}

        dbm = Mock(spec=DatabaseManager)

        expected_data_dict = DataDictType(dbm, CODE, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            location_question = helper.create_question(post, dbm)

        self.create_ddtype_mock.assert_called_once_with(dbm=dbm, name=CODE, slug=SLUG,
                                                        primitive_type=TYPE, description=LABEL)
        self.assertEqual(expected_data_dict, location_question.ddtype)

    def test_should_create_header_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="entity_question", code="ID", name="What is associated entity",
                              language="eng", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        actual_list = helper.get_headers([question1, question2])
        expected_list = ["What is associated entity", "What is your name"]
        self.assertListEqual(expected_list, actual_list)

    def test_should_create_value_list(self):
        data_dictionary = {'Clinic/cid002': {'What is age of father?': 55, 'What is your name?': 'shweta',
                                             "What colour do you choose?": ["red", "blue"],
                                             "what is your loc?": [21.1, 23.3],
                                             'What is associated entity?': 'cid002'},
                           'Clinic/cid001': {'What is age of father?': 35, 'What is your name?': 'asif',
                                             "What colour do you choose?": ["red"], "what is your loc?": [21.1],
                                             'What is associated entity?': 'cid001'}}
        header_list = ["What is associated entity?", "What is your name?", "What is age of father?",
                       "What colour do you choose?", "what is your loc?"]
        actual_list = helper.get_values(data_dictionary, header_list)
        expected_list = [{"entity_name": "cid002", "values": ['shweta', 55, "red,blue", "21.1,23.3"]},
                {"entity_name": "cid001", "values": ['asif', 35, "red", "21.1"]}]
        self.assertListEqual(expected_list, actual_list)

    def test_should_create_type_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = IntegerField(label="number_question", code="ID", name="How many beds",
                                 language="eng", ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        question3 = SelectField(label="multiple_choice_question", code="Q2",
                                options=[("red", 1), ("yellow", 2), ('green', 3)], name="What is your favourite colour",
                                ddtype=ddtype)
        question4 = DateField("What is date", "Q4", "date_question", "mm.yyyy", ddtype)
        actual_list = helper.get_type_list([question1, question2, question3, question4])
        choice_type = copy(helper.MULTI_CHOICE_TYPE_OPTIONS)
        choice_type.extend(
            ["sum(red)", "sum(yellow)", "sum(green)", "percent(red)", "percent(yellow)", "percent(green)"])
        expected_list = [helper.NUMBER_TYPE_OPTIONS, helper.TEXT_TYPE_OPTIONS, choice_type, helper.DATE_TYPE_OPTIONS]
        self.assertListEqual(expected_list, actual_list)

    def test_should_return_aggregates_dictionary(self):
        header_list = ["field1", "field2"]
        post_data = ["Latest", "Sum"]
        expected_dictionary = {"field1": data.reduce_functions.LATEST, "field2": data.reduce_functions.SUM}
        actual_dict = helper.get_aggregate_dictionary(header_list, post_data)
        self.assertEquals(expected_dictionary, actual_dict)

    def test_should_return_aggregates_list(self):
        header_list = ["field1", "field2"]
        post_data = ["Latest", "Sum"]
        actual_list = helper.get_aggregate_list(header_list, post_data)
        self.assertIsInstance(actual_list[0], Latest)
        self.assertIsInstance(actual_list[1], Sum)

    def test_should_create_list_of_values(self):
        data_list = [{"entity_name": "cid002", "values": ['shweta', 55]},
                {"entity_name": "cid001", "values": ['asif', 35]}]
        actual_list = helper.to_report(data_list)
        expected_list = [["cid002", 'shweta', 55], ["cid001", 'asif', 35]]
        self.assertListEqual(expected_list, actual_list)

    def test_should_return_formatted_time_string(self):
        expected_val = "01-01-2011 00:00:00"
        self.assertEquals(expected_val, helper.get_formatted_time_string("01-01-2011 00:00:00"))

    def test_should_remove_default_entity_field(self):
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="entity_question", code="ID", name="What is associated entity",
                              language="eng", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        cleaned_list = helper.hide_entity_question([question1, question2])
        self.assertEquals([question2], cleaned_list)


class TestPreviewCreator(unittest.TestCase):

    def test_should_create_basic_fields_in_preview(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, instruction="please write more tests")
        preview = helper.get_preview_for_field(field)
        self.assertEquals("What's in a name?", preview["description"])
        self.assertEquals("nam", preview["code"])
        self.assertEquals("text", preview["type"])
        self.assertEquals("please write more tests", preview["instruction"])


    def test_should_add_constraint_text_for_text_field_with_min(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraint = TextConstraint(min=10)
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, length=constraint)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10 characters", preview["constraint"])

    def test_should_add_constraint_text_for_text_field_with_max(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraint = TextConstraint(max=100)
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, length=constraint)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100 characters", preview["constraint"])

    def test_should_add_constraint_text_for_text_field_with_max_and_min(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraint = TextConstraint(min=10, max=100)
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, length=constraint)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Between 10 - 100 characters", preview["constraint"])


    def test_should_add_constraint_text_for_numeric_field_with_min(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericConstraint(min=10)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, range=constraint)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10", preview["constraint"])
        self.assertEqual("integer", preview["type"])

    def test_should_add_constraint_text_for_numeric_field_with_max(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericConstraint(max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, range=constraint)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100", preview["constraint"])

    def test_should_add_constraint_text_for_numeric_field_with_max_and_min(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericConstraint(min=10, max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, range=constraint)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("10 - 100", preview["constraint"])

    def test_should_return_choices(self):
        type = DataDictType(Mock(DatabaseManager), name="color type")
        field = SelectField(name="What's the color?", code="nam", label="naam", ddtype=type,
                            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select1", preview["type"])
        self.assertEqual(["Red", "Green", "Blue"], preview["constraint"])

    def test_should_return_choices_type_as_select(self):
        type = DataDictType(Mock(DatabaseManager), name="color type")
        field = SelectField(name="What's the color?", code="nam", label="naam", ddtype=type,
                            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")], single_select_flag=False)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select", preview["type"])

    def test_should_return_date_format(self):
        type = DataDictType(Mock(DatabaseManager), name="date type")
        field = DateField(name="What is the date?", code="dat", label="naam", ddtype=type, date_format="dd/mm/yyyy")
        preview = helper.get_preview_for_field(field)
        self.assertEqual("dd/mm/yyyy", preview["constraint"])

    def test_should_return_blank_in_other_cases(self):
        type = DataDictType(Mock(DatabaseManager), name="date type")
        field = GeoCodeField(name="What is the place?", code="dat", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraint"])

