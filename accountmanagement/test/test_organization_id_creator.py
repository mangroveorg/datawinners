# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from datawinners.accountmanagement.organization_id_creator import  OrganizationIdCreator

class TestOrganizationIdCreator(unittest.TestCase):

    def test_creation_of_organization_id(self):
        id_creator = OrganizationIdCreator()
        id1 = id_creator.generateId()
        id2 = id_creator.generateId()
        self.assertTrue(id1)
        self.assertTrue(id2)
        self.assertFalse(id1==id2)

