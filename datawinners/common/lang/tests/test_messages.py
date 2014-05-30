import unittest

from mangrove.utils.test_utils.database_utils import uniq
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager

from datawinners.common.lang.messages import save_questionnaire_custom_messages


class TestCustomizedMessages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_name = uniq('mangrove-test')
        cls.dbm = get_db_manager('http://localhost:5984/', cls.db_name)

    @classmethod
    def tearDownClass(cls):
        cls.dbm = get_db_manager('http://localhost:5984/', cls.db_name)
        _delete_db_and_remove_db_manager(cls.dbm)

    def test_questionnaire_message_save(self):
        save_questionnaire_custom_messages(self.dbm, "en_test", {"err1":"Invalid submission","err2":"Invalid submission2"},"English")
        msg = self.dbm.database.get("en_test")["messages"]["err1"]
        self.assertEqual("Invalid submission", msg)
        self.check_update_questionnaire_message()

    def check_update_questionnaire_message(self):
        save_questionnaire_custom_messages(self.dbm, "en_test", {"err1": "New Error Message."},"English")
        msg = self.dbm.database.get("en_test")["messages"]["err1"]
        self.assertEqual("New Error Message.", msg)
