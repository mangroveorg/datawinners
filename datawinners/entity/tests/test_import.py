# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from unittest import SkipTest

from mock import Mock, patch

from mangrove.datastore.datadict import get_or_create_data_dict
from mangrove.datastore.entity_type import define_type
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from mangrove.bootstrap import initializer
from mangrove.datastore.queries import get_entity_count_for_type
from datawinners.entity.import_data import import_data
from datawinners.accountmanagement.models import Organization


FORM_CODE = 'cli01'

@SkipTest
class TestImport(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        self.csv_data = """
"form_code","t","n","l","g","d","s","m"
"REG","reporter","Aàman Farafangana ","Farafangana ","-21.8  46.8333","This is a Clinic in near to Farafangana ","r1",987654328
"REG","reporter","Reporter1 Fianarantsoa ","mahajanga ","-20.45  45.1","C'est une clinique à Fianarantsoa","r2",987654329
"REG","reporter","Reporter2 Maintirano ","Maintirano ","-18.05  44.0333","This is a reporter in Maintirano ","r3",987654333
"REG","reporter","Reporter3 Mananjary ","Mananjary ","-21.2  48.3667","This is a reporter in Mananjary ","r4",987654334
"""
        self.csv_data_without_short_code = """
"form_code","t","n","l","g","d","m"
"REG","reporter","Aàman Farafangana ","Farafangana ","-21.8  46.8333","This is a Clinic in near to Farafangana ",987654328
"REG","reporter","Reporter1 Fianarantsoa ","mahajanga ","-20.45  45.1","C'est une clinique à Fianarantsoa",987654329
"REG","reporter","Reporter2 Maintirano ","Maintirano ","-18.05  44.0333","This is a reporter in Maintirano ",987654333
"REG","reporter","Reporter3 Mananjary ","Mananjary ","-21.2  48.3667","This is a reporter in Mananjary ",987654334
"""
        self.csv_subjects_data = """
"form_code","q1","q2"
"cli01","Aàman Farafangana ","Farafangana "
"cli01","Reporter1 Fianarantsoa ","mahajanga "
"cli01","Reporter2 Maintirano ","Maintirano "
"cli01","Reporter3 Mananjary ","Mananjary "
"""
        self.csv_subjects_data_with_error_form_code = """
"form_code","q1","q2"
"cli1","Aàman Farafangana ","Farafangana "
"cli1","Reporter1 Fianarantsoa ","mahajanga "
"cli1","Reporter2 Maintirano ","Maintirano "
"cli1","Reporter3 Mananjary ","Mananjary "
"""
        initializer.run(self.manager)

    def tearDown(self):
        MangroveTestCase.tearDown(self)

    def test_should_import_data_senders(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_data
        organization = Mock(spec=Organization)
        with patch("datawinners.utils.get_organization_from_manager") as get_organization_from_dbm_mock:
            get_organization_from_dbm_mock.return_value = Mock(return_value=organization)
            with patch("datawinners.utils.get_organization") as get_organization:
                mock = Mock(return_value=organization)
                mock.org_id = 'abc'
                get_organization.return_value = mock
                error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                                 manager=self.manager)
                self.assertEqual(4, get_entity_count_for_type(self.manager, entity_type="reporter"))
                self.assertEqual(4, len(imported_entities))
                self.assertEqual('reporter', imported_entities["r1"])
                self.assertEqual('reporter', imported_entities["r2"])
                self.assertEqual('reporter', imported_entities["r3"])
                self.assertEqual('reporter', imported_entities["r4"])

    def test_should_generate_short_code_and_import_data_senders_if_short_code_is_not_given(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_data_without_short_code
        organization = Mock(spec=Organization)
        with patch("datawinners.utils.get_organization_from_manager") as get_organization_from_dbm_mock:
            with patch("datawinners.utils.get_organization") as get_organization:
                mock = Mock(return_value=organization)
                mock.org_id = 'abc'
                get_organization.return_value = mock
                get_organization_from_dbm_mock.return_value = Mock(return_value=organization)

                error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                                 manager=self.manager,
                                                                                                 form_code='form_code')
                self.assertEqual(4, get_entity_count_for_type(self.manager, entity_type="reporter"))
                self.assertEqual(4, len(imported_entities))
                self.assertEqual('reporter', imported_entities["rep1"])
                self.assertEqual('reporter', imported_entities["rep2"])
                self.assertEqual('reporter', imported_entities["rep3"])
                self.assertEqual('reporter', imported_entities["rep4"])

    def create_form_for_entity_type(self):
        string_data_type = get_or_create_data_dict(self.manager, name='Name', slug='name', primitive_type='string')
        school_name_field = TextField(name="name", code="q1", label="What's the name?", ddtype=string_data_type)
        address_field = TextField(name="address", code="q2", label="Where is the clinic?", ddtype=string_data_type)
        unique_id_field = TextField(name="unique_id", code="q3", label="What is the clinic's Unique ID Number?",
                                    ddtype=string_data_type, entity_question_flag=True)
        form_model = FormModel(self.manager, "clinic", form_code=FORM_CODE, entity_type=["clinic"],
                               is_registration_model=True,
                               fields=[school_name_field, address_field, unique_id_field])
        form_model.save()

    def test_should_import_subjects(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_subjects_data
        organization = Mock(spec=Organization)
        entity_type = "clinic"
        define_type(self.manager, [entity_type])
        self.create_form_for_entity_type()
        with patch("datawinners.utils.get_organization_from_manager") as get_organization_from_dbm_mock:
            get_organization_from_dbm_mock.return_value = Mock(return_value=organization)
            with patch("datawinners.utils.get_organization") as get_organization:
                mock = Mock(return_value=organization)
                mock.org_id = 'abc'
                get_organization.return_value = mock
                error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                                 manager=self.manager)
                self.assertEqual(4, get_entity_count_for_type(self.manager, entity_type=entity_type))
                self.assertEqual(4, len(imported_entities))
                self.assertEqual(entity_type, imported_entities["cli1"])
                self.assertEqual(entity_type, imported_entities["cli2"])
                self.assertEqual(entity_type, imported_entities["cli3"])
                self.assertEqual(entity_type, imported_entities["cli4"])

    def test_should_import_subjects_with_form_code(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_subjects_data
        organization = Mock(spec=Organization)
        entity_type = "clinic"
        define_type(self.manager, [entity_type])
        self.create_form_for_entity_type()
        with patch("datawinners.utils.get_organization_from_manager") as get_organization_from_dbm_mock:
            get_organization_from_dbm_mock.return_value = Mock(return_value=organization)
            with patch("datawinners.utils.get_organization") as get_organization:
                mock = Mock(return_value=organization)
                mock.org_id = 'abc'
                get_organization.return_value = mock
                error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                                 manager=self.manager,
                                                                                                 form_code=FORM_CODE)
                self.assertEqual(4, get_entity_count_for_type(self.manager, entity_type=entity_type))
                self.assertEqual(4, len(imported_entities))
                self.assertEqual(entity_type, imported_entities["cli1"])
                self.assertEqual(entity_type, imported_entities["cli2"])
                self.assertEqual(entity_type, imported_entities["cli3"])
                self.assertEqual(entity_type, imported_entities["cli4"])

    def test_should_import_subjects_with_wrong_form_code(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_subjects_data_with_error_form_code
        organization = Mock(spec=Organization)
        entity_type = "clinic"
        define_type(self.manager, [entity_type])
        self.create_form_for_entity_type()
        with patch("datawinners.utils.get_organization_from_manager") as get_organization_from_dbm_mock:
            get_organization_from_dbm_mock.return_value = Mock(return_value=organization)
            with patch("datawinners.utils.get_organization") as get_organization:
                mock = Mock(return_value=organization)
                mock.org_id = 'abc'
                get_organization.return_value = mock
                error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                                 manager=self.manager,
                                                                                                 form_code=FORM_CODE)
                self.assertEqual(0, len(imported_entities))
                self.assertEqual('The file you are uploading is not a list of [clinic]. Please check and upload again.',
                                 error_message)
