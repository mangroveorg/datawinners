import unittest

from mock import patch, Mock

from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException, DatasenderIsNotLinkedException
from datawinners.project.models import Project
from mangrove.form_model.form_model import FormModel, EntityFormModel
from datawinners.submission.submission_utils import PostSMSProcessorCheckDSIsLinkedToProject


class TestPostSMSProcessorCheckDSIsLinkedToProject(unittest.TestCase):
    def setUp(self):
        self.language = 'fr'
        self.patcher = patch('datawinners.submission.submission_utils.get_form_model_by_code')
        self.form_model_patch = self.patcher.start()
        self.project_patcher = patch.object(Project, 'from_form_model')
        self.project_mock = self.project_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.project_patcher.stop()

    def _get_form_model_mock(self, is_registration_form, fields, entity_question =None):
        form_model_mock = Mock(spec=EntityFormModel) if is_registration_form else Mock(spec=FormModel)
        form_model_mock.is_entity_registration_form.return_value = is_registration_form
        form_model_mock.fields = fields
        return form_model_mock

    def _get_project_mock(self):
        project = Mock(spec=Project)
        project.data_senders = ['rep2']
        return project

    def test_should_raise_no_exception_if_ds_is_linked_and_number_of_answers_is_correct(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2])
        self.project_mock.return_value = self._get_project_mock()
        reporter_entity = Mock()
        reporter_entity.short_code = 'rep2'
        incoming_request = {'reporter_entity': reporter_entity}
        processor = PostSMSProcessorCheckDSIsLinkedToProject(dbm=None, request=incoming_request)
        response = processor.process("form_code", {'q1': 'ans', 'q2': 'ans2'})
        self.assertEqual(None, response)

    def test_should_raise_number_of_response_exception_if_number_of_responses_is_incorrect_and_datasender_is_linked(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2])
        self.project_mock.return_value = self._get_project_mock()
        reporter_entity = Mock()
        reporter_entity.short_code = 'rep2'
        incoming_request = {'reporter_entity': reporter_entity, 'exception': SMSParserWrongNumberOfAnswersException('form_code')}
        processor = PostSMSProcessorCheckDSIsLinkedToProject(dbm=None, request=incoming_request)
        self.assertRaises(SMSParserWrongNumberOfAnswersException, processor.process, "form_code", {'q1': 'ans', 'q2': 'ans2'})

    def test_should_raise_datasender_not_linked_exception_if_number_of_responses_is_incorrect_and_datasender_is_not_linked(self):
        self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2])
        self.project_mock.return_value = self._get_project_mock()
        reporter_entity = Mock()
        reporter_entity.short_code = 'rep23'
        incoming_request = {'reporter_entity': reporter_entity, 'exception': SMSParserWrongNumberOfAnswersException('form_code')}
        processor = PostSMSProcessorCheckDSIsLinkedToProject(dbm=None, request=incoming_request)
        self.assertRaises(DatasenderIsNotLinkedException, processor.process, "form_code", {'q1': 'ans', 'q2': 'ans2'})

    #def test_should_not_raise_exception_if_number_of_responses_is_correct_and_datasender_is_not_linked(self):
    #    self.form_model_patch.return_value = self._get_form_model_mock(is_registration_form=False, fields=[1, 2])
    #    self.project_mock.return_value = self._get_project_mock()
    #    reporter_entity = Mock()
    #    reporter_entity.short_code = 'rep23'
    #    incoming_request = {'reporter_entity': reporter_entity}
    #    processor = PostSMSProcessorCheckDSIsLinkedToProject(dbm=None, request=incoming_request)
    #
    #    response = processor.process("form_code", {'q1': 'ans', 'q2': 'ans2'})
    #
    #    self.assertNotEqual(None, response)
    #    self.assertEqual(NOT_AUTHORIZED_DATASENDER_MSG, response.errors)