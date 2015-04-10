import unittest
from mangrove.datastore.documents import ContactDocument


class TestAddToGroup(unittest.TestCase):

    def test_to_add_existing_contacts_to_groups(self):
        group_name = 'group_name1'
        contact_doc = ContactDocument()

        del(contact_doc._data['custom_groups'])

        contact_doc.add_custom_group(group_name)

        self.assertEquals(contact_doc.custom_groups, [group_name])

    def test_to_add_contacts_to_groups(self):
        group_name = 'group_name2'
        contact_doc = ContactDocument()

        contact_doc.add_custom_group(group_name)

        self.assertEquals(contact_doc.custom_groups, [group_name])