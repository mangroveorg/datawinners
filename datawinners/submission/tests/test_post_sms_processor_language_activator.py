import unittest
from django.utils import translation
from mock import patch, Mock
from mangrove.form_model.form_model import FormModel
from datawinners.submission.submission_utils import PostSMSProcessorLanguageActivator

class TestPostSMSProcessorLanguageActivator(unittest.TestCase):
    def setUp(self):
        self.language = 'fr'
        self.patcher = patch('datawinners.submission.submission_utils.get_form_model_by_code')
        get_form_model_mock = self.patcher.start()
        get_form_model_mock.return_value=self.mocked_form_model_active_language(self.language)

    def tearDown(self):
        self.patcher.stop()
        translation.activate('en')

    def test_should_activate_the_language(self):
        mangrove_request = dict()
        form_code = '123'
        PostSMSProcessorLanguageActivator(dbm=None,request=mangrove_request).process(form_code, {})
        self.assertEqual(self.language,translation.get_language())
        self.assertEqual(form_code,mangrove_request['form_code'] )

    def mocked_form_model_active_language(self, language):
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.activeLanguages = [language]
        return form_model_mock
