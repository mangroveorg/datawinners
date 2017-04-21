import unittest
from datawinners.accountmanagement.user_tasks import link_user_to_all_projects
from django.contrib.auth.models import User
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.main.database import get_database_manager
from datawinners.project.couch_view_helper import get_all_projects

class TestLinkUser(unittest.TestCase):

    def setUp(self):
        self.new_user = User(first_name="First", last_name="Last", username="a@b.c")
        self.new_user.save()
        from datawinners.accountmanagement.models import Organization
        org_id = Organization.objects.all()[0].org_id
        self.ngouser = NGOUserProfile(user=self.new_user, org_id=org_id, reporter_id="ds406")
        self.ngouser.save()

    def test_should_link_user_as_datasender_to_all_project(self):
        link_user_to_all_projects(self.new_user.id)
        dbm = get_database_manager(self.new_user)
        all_projects = get_all_projects(dbm)
        for project in all_projects:
            linked_ds = project['value']['datasenders']
            self.assertIn(self.new_user.id, linked_ds)

    def tearDown(self):
        self.ngouser.delete()
        self.new_user.delete()