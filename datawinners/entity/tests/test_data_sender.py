from django.utils.unittest.case import TestCase
from datawinners.entity.data_sender import remove_system_datasenders
from datawinners.entity.view.datasenders import RegisterDatasenderView


class TestDataSender(TestCase):
    def test_remove_test_datasenders(self):
        ds_list = [{"short_code": "non-test"}, {"short_code":"test"}]
        remove_system_datasenders(ds_list)
        self.assertEqual(ds_list, [{"short_code": "non-test"}])


class TestContactRegistration(TestCase):

    def test_should_return_success_message_for_contact_registartion(self):

        project_id = None
        message = "Some success message"

        actual_text = RegisterDatasenderView()._get_success_message_text(message, project_id)

        self.assertEqual(actual_text, "Your contact(s) have been added.")

class TestDataSenderRegistration(TestCase):

    def test_should_return_original_message_when_project_id_is_present(self):

        project_id = '12345'
        message = "Original success message"

        actual_text = RegisterDatasenderView()._get_success_message_text(message, project_id)

        self.assertEqual(actual_text, message)