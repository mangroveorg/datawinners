import unittest
from datawinners.common.lang.messages import save_messages, get_message
from datawinners.main.database import get_db_manager


class TestCustomizedMessages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbm = get_db_manager("hni_testorg_slx364903")

    @classmethod
    def tearDownClass(cls):
        cls.dbm._delete_document(cls.dbm.database.get('en_test'))

    def test_message_save(self):
        save_messages(self.dbm, "en_test", {"err1":"Invalid submission","err2":"Invalid submission2"},"English")
        msg = get_message(self.dbm, "en_test", "err1")
        self.assertEqual("Invalid submission", msg)
        self.check_update_message()

        self.check_fallback_error_message()

    def check_fallback_error_message(self):
        self.assertEqual("Error", get_message(self.dbm, "en_test", "Error"))

    def check_update_message(self):
        save_messages(self.dbm, "en_test", {"err1": "New Error Message."},"English")
        msg = get_message(self.dbm, "en_test", "err1")
        self.assertEqual("New Error Message.", msg)
