import unittest
from datawinners.entity.group_helper import create_new_group
from mock import Mock

class CreateGroupTest(unittest.TestCase):
    
    def test_should_not_add_all_contacts_as_group_name(self):
        dbm = Mock()
        group_names = ["aLl ConTActs", "tous les CONTACTs"]
        for group in group_names:
            success, msg = create_new_group(dbm, group)
            self.assertFalse(success)
            self.assertEqual(u'Group with same name already exits.', msg)