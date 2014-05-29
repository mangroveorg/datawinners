from collections import OrderedDict
import unittest
from mock import Mock, patch
from mangrove.datastore.database import DatabaseManager
from datawinners.common.lang.utils import questionnaire_customized_message_details
from datawinners.main.database import get_db_manager


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)

    def test_should_create_customized_message_dictionary(self):
        custom_messages = OrderedDict()
        custom_messages.update({"reply_success_submission": "Thank you for submission"})
        custom_messages.update({"reply_incorrect_answers": "Check your submission for errors"})
        custom_messages.update({"reply_incorrect_number_of_responses": "Your submission has incorrect number of answers"})
        custom_messages.update({"reply_identification_number_not_registered": "This identification number is not registered"})
        custom_messages.update({"reply_ds_not_authorized": "You are not authorized to send data"})

        DATA_FROM_DB = [{"id": "English", "key": "English",
                        "value": "English", "doc": {'_id': 'English', 'language_name': "English", 'messages':custom_messages}}]

        with patch.object(self.dbm, "load_all_rows_in_view") as load_all_rows_in_view:
            load_all_rows_in_view.return_value = DATA_FROM_DB
            details_list = questionnaire_customized_message_details(self.dbm, "English")
            self.assertEquals(details_list.__len__(),5)
            self.assertEquals(details_list[0],{"title":"Successful Submission","message":"Thank you for submission","code":"reply_success_submission"})



