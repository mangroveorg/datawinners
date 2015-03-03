from unittest import TestCase
from datawinners.entity.data_sender import remove_system_datasenders
from datawinners.entity.view.datasenders import RegisterDatasenderView


class TestDataSender(TestCase):
    def test_remove_test_datasenders(self):
        ds_list = [{"short_code": "non-test"}, {"short_code":"test"}]
        remove_system_datasenders(ds_list)
        self.assertEqual(ds_list, [{"short_code": "non-test"}])


class TestContactRegistration(TestCase):

    def test_should_return_success_message_for_successful_contact_registration(self):

        project_id = None
        message = "Some success message"

        actual_text = RegisterDatasenderView()._get_message_text(message, project_id, True)

        self.assertEqual(actual_text, "Your contact(s) have been added.")

    def test_should_return_error_message_as_is_for_unsuccessful_contact_registration(self):

        project_id = None
        message = "Some error message"

        actual_text = RegisterDatasenderView()._get_message_text(message, project_id, False)

        self.assertEqual(actual_text, "Some error message")


class TestDataSenderRegistration(TestCase):

    def test_should_return_original_message_when_project_id_is_present_for_successful_data_sender_registration(self):

        project_id = '12345'
        message = "Original message"

        actual_text = RegisterDatasenderView()._get_message_text(message, project_id, True)

        self.assertEqual(actual_text, message)


    def test_should_return_original_message_when_project_id_is_present_for_unsuccessful_data_sender_registration(self):

        project_id = '12345'
        message = "Original message"

        actual_text = RegisterDatasenderView()._get_message_text(message, project_id, False)

        self.assertEqual(actual_text, message)