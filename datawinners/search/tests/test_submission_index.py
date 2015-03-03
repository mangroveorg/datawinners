import unittest

import elasticutils
from mock import Mock, patch, MagicMock, PropertyMock

from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity, Contact
from mangrove.form_model.field import TextField, GeoCodeField, SelectField, DateField, UniqueIdField, FieldSet
from mangrove.form_model.form_model import FormModel
from datawinners.search.submission_index import _update_with_form_model_fields, \
    update_submission_search_for_subject_edition, _lookup_contact_by_uid
from mangrove.datastore.documents import SurveyResponseDocument, FormModelDocument


def get_by_short_code_include_voided_mock_func(dbm, unique_code, unique_type):
    entity = Entity(dbm, short_code=unique_code, entity_type=unique_type[0])
    entity._doc.data['name'] = {'value': 'my_clinic'}
    return entity


class TestSubmissionIndex(unittest.TestCase):
    def setUp(self):
        self.form_model = MagicMock(spec=FormModel, id="1212")
        self.field1 = UniqueIdField(unique_id_type='clinic', name='unique_id', code="q1", label='which clinic')
        self.field2 = TextField('text', "q2", "enter text")
        self.field3 = GeoCodeField('gps', "q3", "enter gps")
        self.field4 = SelectField('select', 'q4', 'select multple options',
                                  [{'text': 'one', 'val': 'a'}, {'text': 'two', 'val': 'b'}], single_select_flag=False)
        self.field5 = DateField('date', 'q5', 'enter date', 'mm.dd.yyyy')
        self.field6 = SelectField('select', 'single-select', 'select one option',
                                  [{'text': 'one', 'val': 'a'}, {'text': 'two', 'val': 'b'}], single_select_flag=True)
        self.repeat_question = FieldSet(name="repeat", code="repeat-code", label="repeat-label", fieldset_type="repeat",
                                        field_set=[self.field4, self.field6])
        self.group_question = FieldSet(name="group", code="group-code", label="group-label", fieldset_type="group",
                                       field_set=[self.field4, self.field6])

        self.dbm = MagicMock(spec=DatabaseManager)


    def test_should_update_search_dict_with_form_field_questions_for_success_submissions(self):
        search_dict = {}
        self.form_model.fields = [self.field4]
        values = {
            'q4': "ab"
        }
        submission_doc = SurveyResponseDocument(values=values, status="success")
        self.form_model.get_field_by_code_and_rev.return_value = self.field4
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'clinic1'

            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)

            self.assertEquals(
                {
                    '1212_q4': ['one', 'two'], 'is_anonymous': False,
                    'void': False}, search_dict)

    def test_should_update_search_dict_with_form_field_questions_for_error_submissions(self):
        search_dict = {}
        self.form_model.fields = [self.field1, self.field2, self.field3]
        values = {'q1': 'test_id', 'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = SurveyResponseDocument(values=values, status="error")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'test1'
            _update_with_form_model_fields(None, submission_doc, search_dict, self.form_model)
            self.assertEquals(
                {'1212_q1': 'test1', "1212_q1_unique_code": "test_id", '1212_q2': 'wrong number',
                 '1212_q3': 'wrong text', 'is_anonymous': False,
                 'void': False},
                search_dict)

    def test_should_not_update_search_dict_with_uid_field(self):
        search_dict = {}
        self.form_model.fields = [self.field1, self.field2, self.field3]
        values = {'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = SurveyResponseDocument(values=values, status="error")
        _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
        self.assertEquals(
            {'1212_q2': 'wrong number', '1212_q3': 'wrong text', 'is_anonymous': False,
             'void': False},
            search_dict)

    def test_should_update_search_dict_with_select_field_in_field_set(self):
        search_dict = {}
        self.form_model.fields = [self.repeat_question]
        values = {'repeat-code': [{'q4': 'a b', 'single-select': 'a'}]}
        submission_doc = SurveyResponseDocument(values=values, status="success")
        _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
        self.assertEquals(
            {'1212_repeat-code': '[{"single-select": "one", "q4": ["one", "two"]}]', 'is_anonymous': False,
             'void': False},
            search_dict)

    def test_should_update_search_dict_with_select_field_in_group_within_repeat(self):
        search_dict = {}
        self.form_model.fields = [
            FieldSet(name="repeat", code="repeat-code", label="repeat-label", fieldset_type="repeat",
                     field_set=[self.group_question])]
        values = {'repeat-code': [{'group-code': [{'q4': 'a b', 'single-select': 'a'}]}]}
        submission_doc = SurveyResponseDocument(values=values, status="success")
        _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
        self.assertEquals(
            {'1212_repeat-code': '[{"group-code": [{"single-select": "one", "q4": ["one", "two"]}]}]',
             'is_anonymous': False,
             'void': False},
            search_dict)

    def test_should_update_search_dict_with_select_field_in_group(self):
        search_dict = {}
        self.form_model.fields = [self.group_question]
        values = {'group-code': [{'q4': 'a b', 'single-select': 'a'}]}
        submission_doc = SurveyResponseDocument(values=values, status="success")
        self.form_model.get_field_by_code_and_rev.side_effect = lambda code, revision: \
            {"q4": self.field4, "single-select": self.field6}[code]
        _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
        self.assertEquals(
            {'void': False, '1212_group-code-single-select': 'one', '1212_group-code-q4': ['one', 'two'],
             'is_anonymous': False},
            search_dict)

    def test_should_update_submission_index_date_field_with_current_format(self):
        self.form_model.fields = [self.field1, self.field5]
        values = {'q1': 'cid005',
                  'q5': '12.2012'}
        submission_doc = SurveyResponseDocument(values=values, status="success", form_model_revision="rev1")
        search_dict = {}
        self.form_model._doc = Mock(spec=FormModelDocument)
        self.form_model._doc.rev = "rev2"
        self.form_model.get_field_by_code_and_rev.return_value = DateField("q5", "date", "Date", "mm.yyyy")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'Test'
            search_dict = _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict,
                                                         self.form_model)
            self.assertEquals("12.01.2012", search_dict.get("1212_q5"))


    def test_should_update_entity_field_in_submission_index(self):
        self.dbm.database_name = 'db_name'
        entity_type = ['clinic']
        short_code = 'cli001'
        last_name = 'bangalore'
        with patch(
                "datawinners.search.submission_index._get_submissions_for_unique_id_entry") as _get_submissions_for_unique_id_entry_mock:
            with patch.object(self.dbm, "load_all_rows_in_view") as load_all_rows_in_view:
                load_all_rows_in_view.return_value = [{'doc': {'name': "project name", "form_code": "cli001",
                                                               "json_fields": [
                                                                   {"name": "unique_id_field", "type": "unique_id",
                                                                    "unique_id_type": 'clinic', "code": 'q1'}],
                                                               "_id": "form_model_id"}}]
                survey_response_index1 = Mock(_id='id1')
                filtered_query = Mock(spec=elasticutils.S)
                filtered_query.all.return_value = [survey_response_index1]

                submission1 = Mock()
                submission1._id = "id1"
                query_mock = Mock()
                query_mock.values_dict.return_value = [submission1]
                _get_submissions_for_unique_id_entry_mock.return_value = query_mock

                with patch.object(SubmissionIndexUpdateHandler,
                                  'update_field_in_submission_index') as update_field_in_submission_index:
                    update_submission_search_for_subject_edition(self.dbm, entity_type, short_code, last_name)

                    # _get_submissions_for_unique_id_entry_mock.assert_called_with(**{'form_model_id_q1_unique_code': 'cli001'})
                    update_field_in_submission_index.assert_called_with('id1', {'form_model_id_q1': 'bangalore'})


    def test_should_get_comma_separated_list_if_field_changed_from_choice_to_unique_id(self):
        search_dict = {}

        options = [{'text': 'option1', 'val': 'a'}, {'text': 'option2', 'val': 'b'}]

        self.form_model.fields = [self.field1]
        original_field = SelectField('selectField', 'q1', 'q1', options)
        self.form_model.get_field_by_code_and_rev.return_value = original_field
        values = {'q1': 'ab', 'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = SurveyResponseDocument(values=values, status="error")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'N/A'

            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
            self.assertEquals(
                {'1212_q1': 'N/A', '1212_q1_unique_code': 'option1,option2', 'is_anonymous': False, 'void': False},
                search_dict)

    def test_generate_elastic_index_for_a_unique_id_field_in_parent_level(self):
        search_dict = {}
        self.form_model.fields = [UniqueIdField('clinic', 'my_unique_id', 'my_unique_id', 'My Unique ID')]
        value = {'my_unique_id': 'cli001'}
        submission = SurveyResponseDocument(values=value, status='success')
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'my_clinic'
            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission, search_dict, self.form_model)
            self.assertEqual(search_dict, {'1212_my_unique_id': 'my_clinic', '1212_my_unique_id_unique_code': 'cli001',
                                           'is_anonymous': False, 'void': False})

    def test_generate_elastic_index_for_a_unique_id_field_within_group(self):
        search_dict = {}
        unique_id_field = UniqueIdField('clinic', 'my_unique_id', 'my_unique_id', 'My Unique ID')
        group_field = FieldSet('group_name', 'group_name', 'My Label', field_set=[unique_id_field])
        self.form_model.fields = [group_field]
        value = {'group_name': [{'my_unique_id': 'cli001'}]}
        submission = SurveyResponseDocument(values=value, status='success')
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'my_clinic'
            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission, search_dict, self.form_model)
            self.assertEqual(search_dict, {'1212_group_name-my_unique_id': 'my_clinic',
                                           '1212_group_name-my_unique_id_unique_code': 'cli001', 'is_anonymous': False,
                                           'void': False})


    def test_generate_elastic_index_for_a_unique_id_field_within_repeat(self):
        search_dict = {}
        unique_id_field = UniqueIdField('clinic', 'my_unique_id', 'my_unique_id', 'My Unique ID')
        group_field = FieldSet('repeat_name', 'repeat_name', 'My Label', field_set=[unique_id_field],
                               fieldset_type='repeat')
        self.form_model.fields = [group_field]
        value = {'repeat_name': [{'my_unique_id': 'cli001'}, {'my_unique_id': 'cli002'}]}
        submission = SurveyResponseDocument(values=value, status='success')

        with patch(
                'datawinners.search.submission_index.get_by_short_code_include_voided') as get_by_short_code_include_voided_mock:
            get_by_short_code_include_voided_mock.side_effect = get_by_short_code_include_voided_mock_func
            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission, search_dict, self.form_model)
            self.assertDictEqual(search_dict, {
                '1212_repeat_name': '[{"my_unique_id": "my_clinic", "my_unique_id_unique_code": "cli001"}, '
                                    '{"my_unique_id": "my_clinic", "my_unique_id_unique_code": "cli002"}]',
                'is_anonymous': False, 'void': False, })

    def test_generate_elastic_index_for_a_unique_id_field_within_repeat_in_group(self):
        unique_id_field = UniqueIdField('clinic', 'my_unique_id', 'my_unique_id', 'My Unique ID')
        repeat_field = FieldSet('repeat_name', 'repeat_name', 'My Label', field_set=[unique_id_field],
                                fieldset_type='repeat')
        group_field = FieldSet('group_name', 'group_name', 'My Label', field_set=[repeat_field], fieldset_type='group')
        self.form_model.fields = [group_field]
        value = {'group_name': [{'repeat_name': [{'my_unique_id': 'cli001'}, {'my_unique_id': 'cli002'}]}]}
        submission = SurveyResponseDocument(values=value, status='success')

        search_dict = {}
        with patch(
                'datawinners.search.submission_index.get_by_short_code_include_voided') as get_by_short_code_include_voided_mock:
            get_by_short_code_include_voided_mock.side_effect = get_by_short_code_include_voided_mock_func
            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission, search_dict, self.form_model)
            self.assertDictEqual(search_dict, {
                '1212_group_name-repeat_name': '[{"my_unique_id": "my_clinic", "my_unique_id_unique_code": "cli001"}, '
                                               '{"my_unique_id": "my_clinic", "my_unique_id_unique_code": "cli002"}]',
                'is_anonymous': False, 'void': False, })

    def test_generate_elastic_index_for_a_unique_id_field_within_group_in_repeat(self):
        unique_id_field = UniqueIdField('clinic', 'my_unique_id', 'my_unique_id', 'My Unique ID')
        group_field = FieldSet('group_name', 'group_name', 'My Label', field_set=[unique_id_field],
                               fieldset_type='group')
        repeat_field = FieldSet('repeat_name', 'repeat_name', 'My Label', field_set=[group_field],
                                fieldset_type='repeat')
        self.form_model.fields = [repeat_field]
        value = {
            'repeat_name': [{'group_name': [{'my_unique_id': 'cli001'}]}, {'group_name': [{'my_unique_id': 'cli002'}]}]}
        submission = SurveyResponseDocument(values=value, status='success')

        search_dict = {}
        with patch(
                'datawinners.search.submission_index.get_by_short_code_include_voided') as get_by_short_code_include_voided_mock:
            get_by_short_code_include_voided_mock.side_effect = get_by_short_code_include_voided_mock_func
            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission, search_dict, self.form_model)
            self.assertDictEqual(search_dict, {
                '1212_repeat_name': '[{"group_name": [{"my_unique_id": "my_clinic", "my_unique_id_unique_code": "cli001"}]}, '
                                    '{"group_name": [{"my_unique_id": "my_clinic", "my_unique_id_unique_code": "cli002"}]}]',
                'is_anonymous': False, 'void': False, })

    def test_generate_elastic_index_for_a_unique_id_field_within_group_in_group(self):
        unique_id_field = UniqueIdField('clinic', 'my_unique_id', 'my_unique_id', 'My Unique ID')
        group1_field = FieldSet('group1_name', 'group1_name', 'My Label', field_set=[unique_id_field],
                               fieldset_type='group')
        group2_field = FieldSet('group2_name', 'group2_name', 'My Label', field_set=[group1_field],
                                fieldset_type='group')
        self.form_model.fields = [group2_field]
        value = {
            'group2_name': [{'group1_name': [{'my_unique_id': 'cli001'}]}]}
        submission = SurveyResponseDocument(values=value, status='success')

        search_dict = {}
        with patch(
                'datawinners.search.submission_index.get_by_short_code_include_voided') as get_by_short_code_include_voided_mock:
            get_by_short_code_include_voided_mock.side_effect = get_by_short_code_include_voided_mock_func
            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission, search_dict, self.form_model)
            self.assertDictEqual(search_dict, {
                "1212_group1_name-my_unique_id": "my_clinic", "1212_group1_name-my_unique_id_unique_code": "cli001",
                'is_anonymous': False, 'void': False, })

    def test_should_get_name_and_short_code_of_contact(self):
        dbm = MagicMock(spec=DatabaseManager)
        uuid = "ds_short_code"
        contact = Mock(spec=Contact)
        contact.value.return_value = "ds_name"
        contact.short_code = uuid

        with patch('datawinners.search.submission_index.Contact') as contact_mock:
            contact_mock.get.return_value = contact
            name, short_code = _lookup_contact_by_uid(dbm, uuid)

            self.assertEqual(name, "ds_name")
            self.assertEqual(short_code, "ds_short_code")

    def test_should_get_phone_number_and_short_code_of_contact_when_name_does_not_exist(self):
        dbm = MagicMock(spec=DatabaseManager)
        uuid = "ds_short_code"
        mobile_number = "some_number"

        contact = Mock(spec=Contact)
        contact.value('name').return_value = None
        contact.value('mobile_number').return_value = 'some_number'
        contact.short_code = uuid

        with patch('datawinners.search.submission_index.Contact') as contact_mock:
            contact_mock.get.return_value = contact
            number, short_code = _lookup_contact_by_uid(dbm, uuid)

            self.assertEqual(mobile_number, "some_number")
            self.assertEqual(short_code, "ds_short_code")