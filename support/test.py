from unittest import TestCase
from find_organization_by_project_id import find_organization

class TestMigrate(TestCase):
    def test_find_organization(self):
        find_organization()
