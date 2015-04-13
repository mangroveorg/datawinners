import unittest
from mangrove.datastore.documents import ContactDocument


class ContactDocumentTest(unittest.TestCase):

    def test_to_add_existing_contacts_to_groups(self):
        group_name = 'group_name1'
        contact_doc = ContactDocument()

        contact_doc._data.pop('custom_groups')

        contact_doc.add_custom_group(group_name)

        self.assertEquals(contact_doc.custom_groups, [group_name])

    def test_to_add_contacts_to_groups(self):
        group_name = 'group_name2'
        contact_doc = ContactDocument()

        contact_doc.add_custom_group(group_name)

        self.assertEquals(contact_doc.custom_groups, [group_name])

    def test_should_not_add_duplicate_groups(self):
        contact_doc = ContactDocument()

        contact_doc._data['custom_groups'].append('group2')

        contact_doc.add_custom_group('group2')

        self.assertEquals(contact_doc.custom_groups, ['group2'])


    def test_should_not_remove_existing_groups(self):
        contact_doc = ContactDocument()

        contact_doc._data['custom_groups'].append('group1')

        contact_doc.add_custom_group('group3')

        self.assertEquals(contact_doc.custom_groups, ['group1', 'group3'])

