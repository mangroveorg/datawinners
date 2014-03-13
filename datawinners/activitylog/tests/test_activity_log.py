import unittest
from datetime import datetime, date
from django.contrib.auth.models import User
from django.test import TestCase
from mock import Mock, patch
from datawinners.accountmanagement.models import Organization
from django.db.models.base import ModelState

class TestUserActivityLog(TestCase):

    fixtures = ['test_data.json']

    organization = Mock(spec=Organization)
    organization.org_id = "ABCDXW"
    user = Mock(spec=User)
    user.id = 1
    state = Mock(spec=ModelState)
    state.db = None
    user._state = state

    def setUp(self):
        pass

    def test_should_log_activity(self):
        request = Mock()
        request.user = self.user
        with patch("datawinners.utils.get_organization") as get_organization_mock:
            from datawinners.activitylog.models import UserActivityLog

            get_organization_mock.return_value = self.organization
            UserActivityLog().log(request, detail="Nothing", action="Created Project",
                project="TestCaseProject2Deleted")
            self.matched = UserActivityLog.objects.filter(project="TestCaseProject2Deleted",
                action="Created Project", detail="Nothing")
            inserted = self.matched[0]
            self.assertEquals(len(self.matched), 1)
            self.assertEquals(datetime.strftime(inserted.log_date, "%Y-%m-%d"),
                datetime.strftime(date.today(), "%Y-%m-%d"))
            self.matched.delete()

    def check_detail_parsing(self, data, expected_detail):
        from datawinners.activitylog.models import UserActivityLog

        log = UserActivityLog(**data)

        self.assertEqual(log.translated_detail(), expected_detail)