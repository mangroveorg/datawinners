import unittest
from elasticsearch_dsl.result import Result, Response
from elasticsearch_dsl.utils import AttrDict

from elasticutils import DictSearchResults
from mock import Mock, MagicMock

from datawinners.search.submission_query import SubmissionQueryResponseCreator, \
    _format_fieldset_values_for_representation
from mangrove.form_model.field import UniqueIdField, TextField, IntegerField, SelectField, FieldSet
from mangrove.form_model.form_model import FormModel


class TestSubmissionResponseCreator(unittest.TestCase):
    def test_should_give_back_entries_according_to_header_order(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['some_question', 'ds_id', 'ds_name', 'form_model_id_q1', 'form_model_id_q1_unique_code']
        results = Response({"_hits": [
            Result({'_type': "form_model_id", '_id': 'index_id', '_source': {'ds_id': 'his_id', 'ds_name': 'his_name',
                                                                             'form_model_id_q1_unique_code': 'subject_id',
                                                                             'form_model_id_q1': 'sub_last_name',
                                                                             'some_question': 'answer for it'}})]})
        form_model.entity_questions = [UniqueIdField('Test subject', 'name', 'q1', 'which subject')]
        form_model.id = 'form_model_id'
        local_time_delta = ('+', 2, 0)
        submissions = SubmissionQueryResponseCreator(form_model, local_time_delta).create_response(required_field_names,
                                                                                                   results)

        expected = [['index_id', 'answer for it', ["his_name<span class='small_grey'>  his_id</span>"],
                     ["sub_last_name<span class='small_grey'>  subject_id</span>"]]]
        self.assertEqual(submissions, expected)

    def test_should_give_create_response_with_no_unique_id_fields(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['ds_id', 'ds_name', 'some_question']
        results = Response({"_hits": [
            Result({'_type': "form_model_id", '_id': 'index_id', '_source': {'ds_id': 'his_id', 'ds_name': 'his_name',
                                                                             'some_question': 'answer'}})]})

        form_model.entity_questions = []
        form_model.id = 'form_model_id'
        local_time_delta = ('+', 2, 0)

        submissions = SubmissionQueryResponseCreator(form_model, local_time_delta).create_response(required_field_names,
                                                                                                   results)

        expected = [['index_id', ["his_name<span class='small_grey'>  his_id</span>"], 'answer']]
        self.assertEqual(submissions, expected)

    def test_should_format_repeat_with_multi_select_question(self):
        field1 = TextField(name='name', code='name', label='wat is ur name')
        field2 = IntegerField(name='age', code='age', label='wat is ur age')
        field3 = SelectField(name='languages', code='lang', label='wat languages do you kno',
                             options=[("English US", "eng"), ("French", "fre"), ("German", "ger"), ("Spanish", "spa")],
                             single_select_flag=False)
        multi_field = FieldSet('student_details', 'student_details', 'Enter Student details',
                               field_set=[field1, field2, field3])
        entry = u'[{"name": "messi", "age": "24", "lang": []}, {"name": "ronaldo", "age": "28", "lang": ["English US", "French", "Spanish"]}, {"name": "mueller", "age": "22", "lang": ["German"]}]'
        formatted_values = _format_fieldset_values_for_representation(entry, multi_field)
        result = '<span class="repeat_ans">"<span class="repeat_qtn_label">wat is ur name</span>: messi", "<span class="repeat_qtn_label">wat is ur age</span>: 24", "<span class="repeat_qtn_label">wat languages do you kno</span>: ";<br><br>' \
                 '"<span class="repeat_qtn_label">wat is ur name</span>: ronaldo", "<span class="repeat_qtn_label">wat is ur age</span>: 28", "<span class="repeat_qtn_label">wat languages do you kno</span>: (English US, French, Spanish)";<br><br>' \
                 '"<span class="repeat_qtn_label">wat is ur name</span>: mueller", "<span class="repeat_qtn_label">wat is ur age</span>: 22", "<span class="repeat_qtn_label">wat languages do you kno</span>: German";<br><br></span>'
        self.assertEqual(formatted_values, result)

    def test_should_format_repeat_with_single_select_question(self):
        field1 = TextField(name='name', code='name', label='wat is ur name')
        field2 = IntegerField(name='age', code='age', label='wat is ur age')
        field3 = SelectField(name='languages', code='lang', label='wat languages do you kno',
                             options=[("English US", "eng"), ("French", "fre"), ("German", "ger"), ("Spanish", "spa")],
                             single_select_flag=True)
        multi_field = FieldSet('student_details', 'student_details', 'Enter Student details',
                               field_set=[field1, field2, field3])
        entry = u'[{"name": "messi", "age": "24", "lang": ""}, {"name": "ronaldo", "age": "28", "lang": "English US"}, {"name": "mueller", "age": "22", "lang": "German"}]'
        formatted_values = _format_fieldset_values_for_representation(entry, multi_field)
        result = '<span class="repeat_ans">"<span class="repeat_qtn_label">wat is ur name</span>: messi", "<span class="repeat_qtn_label">wat is ur age</span>: 24", "<span class="repeat_qtn_label">wat languages do you kno</span>: ";<br><br>' \
                 '"<span class="repeat_qtn_label">wat is ur name</span>: ronaldo", "<span class="repeat_qtn_label">wat is ur age</span>: 28", "<span class="repeat_qtn_label">wat languages do you kno</span>: English US";<br><br>' \
                 '"<span class="repeat_qtn_label">wat is ur name</span>: mueller", "<span class="repeat_qtn_label">wat is ur age</span>: 22", "<span class="repeat_qtn_label">wat languages do you kno</span>: German";<br><br></span>'
        self.assertEqual(formatted_values, result)

    def test_should_format_repeat_with_group_question(self):
        field1 = TextField(name='name', code='name', label='wat is ur name')
        field2 = IntegerField(name='age', code='age', label='wat is ur age')
        field3 = SelectField(name='languages', code='lang', label='wat languages do you kno',
                             options=[("English US", "eng"), ("French", "fre"), ("German", "ger"), ("Spanish", "spa")],
                             single_select_flag=False)
        group_field = FieldSet('group', 'group', 'group', field_set=[field1, field2, field3])
        multi_field = FieldSet('student_details', 'student_details', 'Enter Student details',
                               field_set=[group_field])
        entry = u'[{"group":[{"name": "messi", "age": "24", "lang": []}]},{"group": [{"name": "ronaldo", "age": "28", "lang": ["English US", "French", "Spanish"]}]},{"group": [{"name": "mueller", "age": "22", "lang": ["German"]}]}]'
        formatted_values = _format_fieldset_values_for_representation(entry, multi_field)
        result = '<span class="repeat_ans">"<span class="repeat_qtn_label">group</span>: "<span class="repeat_qtn_label">wat is ur name</span>: messi", "<span class="repeat_qtn_label">wat is ur age</span>: 24", "<span class="repeat_qtn_label">wat languages do you kno</span>: ";";<br><br>' \
                 '"<span class="repeat_qtn_label">group</span>: "<span class="repeat_qtn_label">wat is ur name</span>: ronaldo", "<span class="repeat_qtn_label">wat is ur age</span>: 28", "<span class="repeat_qtn_label">wat languages do you kno</span>: (English US, French, Spanish)";";<br><br>' \
                 '"<span class="repeat_qtn_label">group</span>: "<span class="repeat_qtn_label">wat is ur name</span>: mueller", "<span class="repeat_qtn_label">wat is ur age</span>: 22", "<span class="repeat_qtn_label">wat languages do you kno</span>: German";";<br><br></span>'
        self.assertEqual(formatted_values, result)

    def test_should_format_repeat_with_skippable_group_question(self):
        field1 = TextField(name='name', code='name', label='wat is ur name')
        field2 = IntegerField(name='age', code='age', label='wat is ur age')
        field3 = SelectField(name='languages', code='lang', label='wat languages do you kno',
                             options=[("English US", "eng"), ("French", "fre"), ("German", "ger"), ("Spanish", "spa")],
                             single_select_flag=False)
        group_field = FieldSet('group', 'group', 'group', field_set=[field1, field2, field3])
        multi_field = FieldSet('student_details', 'student_details', 'Enter Student details',
                               field_set=[group_field])
        entry = u'[{}]'
        formatted_values = _format_fieldset_values_for_representation(entry, multi_field)
        result = '<span class="repeat_ans">"<span class="repeat_qtn_label">group</span>: ";<br><br></span>'
        self.assertEqual(formatted_values, result)
