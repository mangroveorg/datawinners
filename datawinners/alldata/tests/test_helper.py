# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock
from django.contrib.auth.models import User
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.alldata import helper
from datawinners.alldata.helper import get_all_project_for_user

class TestHelper(unittest.TestCase):

    def setUp(self):
        self.database_manager = helper.get_database_manager
        self.all_projects = helper.models.get_all_projects
        helper.get_database_manager = stub_get_database_manager

    def test_should_return_all_projects(self):
        user = StubUser(NormalGuy())
        helper.models.get_all_projects = stub_get_all_projects
        projects = get_all_project_for_user(user)
        assert projects["project_name"] == "helloworld"

    def test_should_return_all_projects_for_user(self):
        user = StubUser(ReporterProfile())
        helper.models.get_all_projects = stub_get_all_projects_for_reporter
        projects = get_all_project_for_user(user)
        assert projects["project_name"] == "helloworld"

    def test_should_return_disabled_and_display_none_for_reporter(self):
        user = StubUser(ReporterProfile())
        disabled, hide = helper.get_visibility_settings_for(user)
        assert disabled  == 'disable_link_for_reporter'
        assert hide == 'none'

    def test_should_return_enabled_and_display_for_other(self):
        user = StubUser(NormalGuy())
        disabled, hide = helper.get_visibility_settings_for(user)
        assert hide  == ""
        assert disabled == ""

    def tearDown(self):
        helper.models.get_all_projects = self.all_projects
        helper.get_database_manager = self.database_manager



class StubUser(User):

    def __init__(self, profile):
        self.profile= profile

    def get_profile(self):
        return self.profile


class ReporterProfile(NGOUserProfile):

    def __init__(self):
        self.reporter_id = "007"

    @property
    def reporter(self):
        return True


class NormalGuy(NGOUserProfile):

    @property
    def reporter(self):
        return False



def stub_get_database_manager(*args):
    return Mock()

def stub_get_all_projects_for_reporter(*args):
    assert args[0] is not None
    assert args[1] is not None
    return {"project_name": "helloworld"}

def stub_get_all_projects(*args):
    assert args[0] is not None
    return {"project_name": "helloworld"}
