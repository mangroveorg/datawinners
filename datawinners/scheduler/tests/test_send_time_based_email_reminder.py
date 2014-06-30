import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from datawinners import settings
from datawinners.scheduler.scheduler import send_time_based_reminder_email
from datawinners.accountmanagement.models import Organization, OrganizationIdCreator
from datawinners.accountmanagement.utils import get_email_detail_by_type, RELATIVE_DELTA_BY_EMAIL_TYPE
from mock import Mock, patch
from django.contrib.auth.models import User, Group
from datawinners.tests.data import TRIAL_ACCOUNT_ORGANIZATION_ID
from django.template.loader import render_to_string
from django.core import mail
from rest_framework.authtoken.models import Token
from django.contrib.sites.models import Site

class TestSendTimeBasedReminder(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.organization = Organization.objects.get(pk=TRIAL_ACCOUNT_ORGANIZATION_ID)
        users = self.organization.get_related_users()
        self.user = users[0]
        self.group = Group.objects.get(name='NGO Admins')
        self.group.user_set.add(self.user)
        self.token = Token.objects.get_or_create(user=self.user)[0].key

    def tearDown(self):
        Token.objects.filter(user=self.user).delete()
        self.group.user_set.remove(self.user)

    def test_should_send_timebased_emails(self):
        for email_type, delta in RELATIVE_DELTA_BY_EMAIL_TYPE.items():
            active_date = datetime.today() - relativedelta(**delta[0])
            method_name = "get_all_active_trial_organizations" \
                if email_type != 'sixty_days_after_deactivation' else "get_all_deactivated_trial_organizations"
            self.organization.status_changed_datetime = active_date
            self.organization.active_date = active_date
            self.organization.save()
            with patch.object(Organization, method_name, side_effect=self.organizations_side_effect):
                subject, template, sender = get_email_detail_by_type(email_type)
                send_time_based_reminder_email()
                site = Site.objects.get_current()
                email = mail.outbox.pop()
                self.assertEqual(['chinatwu2@gmail.com'], email.to)
                ctx = {'username':'Trial User', 'organization':self.organization, 'site':site,
                       'token': self.token}
                self.assertEqual(render_to_string('email/%s_en.html' % template, ctx), email.body)
                
    def organizations_side_effect(self, active_date__contains=None):
        if datetime.strftime(self.organization.status_changed_datetime, "%Y-%m-%d") == active_date__contains:
            return [self.organization]
        return []
    