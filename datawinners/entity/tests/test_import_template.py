import unittest

from django.http import HttpRequest
from mock import patch, Mock, PropertyMock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel


valid_web_user_patch = patch('datawinners.accountmanagement.decorators.valid_web_user', lambda x: x)
valid_web_user_patch.start()


from datawinners.entity.view.import_template import import_template


class TestImportTemplate(unittest.TestCase):
    def test_should_create_workbook_response_with_subject_headers_when_importing_subjects(self):
        request = HttpRequest()
        request.GET['filename']='file'
        request.user = 'someuser'

        with patch('datawinners.entity.view.import_template.get_database_manager') as get_db_manager:
            with patch('datawinners.entity.view.import_template.get_form_model_by_code') as get_form_model_by_code:
                with patch('datawinners.entity.view.import_template.get_subject_headers') as get_subject_headers:
                    with patch("datawinners.entity.view.import_template.WorkBookResponseFactory") as workbook_response_factory:
                        get_db_manager.return_value = Mock(spec=DatabaseManager)
                        form_model = Mock(spec=FormModel)
                        type(form_model).form_fields = PropertyMock(return_value=[{'code': 'cli001'}])
                        form_model.is_entity_registration_form.return_value = True
                        get_form_model_by_code.return_value = form_model
                        get_subject_headers.return_value = ['What is the subject']
                        workbook_response_factory.return_value = workbook_response_factory

                        import_template(request, '001')

                        workbook_response_factory.assert_called_with('001','file','file')
                        get_subject_headers.assert_called_with([{'code': 'cli001'}])
                        workbook_response_factory.create_workbook_response.assert_called_with([['What is the subject']],['cli001'])

    def test_should_create_workbook_response_with_submission_headers_when_importing_submissions(self):
        request = HttpRequest()
        request.GET['filename']='file%20name'
        request.user = 'someuser'

        with patch('datawinners.entity.view.import_template.get_database_manager') as get_db_manager:
            with patch('datawinners.entity.view.import_template.get_form_model_by_code') as get_form_model_by_code:
                    with patch('datawinners.entity.view.import_template.get_submission_headers') as get_submission_headers:
                        with patch("datawinners.entity.view.import_template.WorkBookResponseFactory") as workbook_response_factory:
                            get_db_manager.return_value = Mock(spec=DatabaseManager)
                            form_model = Mock(spec=FormModel)
                            type(form_model).form_fields = PropertyMock(return_value=[{'code': 'cli001'}])
                            form_model.is_entity_registration_form.return_value = False
                            get_form_model_by_code.return_value = form_model

                            get_submission_headers.return_value = ['What is the submission date']
                            workbook_response_factory.return_value = workbook_response_factory

                            import_template(request, '001')

                            workbook_response_factory.assert_called_with('001','file name','Import_Submissions')
                            get_submission_headers.assert_called_with([{'code': 'cli001'}], form_model)
                            workbook_response_factory.create_workbook_response.assert_called_with([['What is the submission date']],['cli001'])

    valid_web_user_patch.stop()


