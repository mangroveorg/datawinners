from datetime import datetime, timedelta
import dircache
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from mock import patch, Mock
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator
from datawinners.deactivate.deactive import get_creator, get_expired_account_list, create_email, get_creators, send_email, send_deactivate_email


import unittest

class TestDeactivateExpiredAccount(unittest.TestCase):

    def prepare_organization(self):
        self.expired_organization_out_of_31_days = Organization(name='test_org_for_expired_organization_out_of_31_days',
                                                                sector='PublicHealth', address='add',
                                                                city='xian', country='china',
                                                                zipcode='10000', in_trial_mode=True,
                                                                active_date=datetime.today() - timedelta(days=31),
                                                                org_id=OrganizationIdCreator().generateId())
        self.paid_organization = Organization(name='test_org_for_paid_account',
                                              sector='PublicHealth', address='add',
                                              city='xian', country='china',
                                              zipcode='10000', in_trial_mode=False, active_date=datetime(2011, 8, 15),
                                              org_id=OrganizationIdCreator().generateId())
        self.unexpired_organization = Organization(name='test_org_for_unexpired_account',
                                                   sector='PublicHealth', address='add',
                                                   city='xian', country='china',
                                                   zipcode='10000', in_trial_mode=True, active_date=datetime.today(),
                                                   org_id=OrganizationIdCreator().generateId())
        self.expired_organization_of_30_days = Organization(name='test_org_for_expired_organization_of_30_days',
                                                            sector='PublicHealth', address='add',
                                                            city='xian', country='china',
                                                            zipcode='10000', in_trial_mode=True,
                                                            active_date=datetime.today() - timedelta(days=30),
                                                            org_id=OrganizationIdCreator().generateId())
        self.expired_organization_of_30_days.save()
        self.expired_organization_out_of_31_days.save()
        self.unexpired_organization.save()
        self.paid_organization.save()

    def setUp(self):
        self.user1 = User(username='expired1@mail.com', email= 'expired1@mail.com', password='expired',first_name='first_name1',last_name='last_name1')
        self.user2 = User(username='expired2@mail.com', email= 'expired2@mail.com', password='expired',first_name='first_name2',last_name='last_name2')
        self.user1.set_password('expired')
        self.user2.set_password('expired')
        self.user1.save()
        self.user2.save()

        self.prepare_organization()

        NGOUserProfile(user = self.user1,title = 'Mr.',org_id = self.expired_organization_of_30_days.org_id).save()
        NGOUserProfile(user = self.user2,title = 'Ms.',org_id = self.expired_organization_of_30_days.org_id).save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.expired_organization_of_30_days.delete()
        self.expired_organization_out_of_31_days.delete()
        self.unexpired_organization.delete()
        self.paid_organization.delete()

    def test_get_organization_creator_should_return_first_user_of_organization(self):
        self.assertEqual(get_creator(self.expired_organization_of_30_days),self.user1)

    def test_should_not_contain_unexpired_organizations(self):
        organizations = get_expired_account_list()
        self.assertIn(self.expired_organization_of_30_days,organizations)
        self.assertNotIn(self.unexpired_organization,organizations)

    def test_should_not_contain_paid_organizations(self):
        organizations = get_expired_account_list()
        self.assertNotIn(self.paid_organization, organizations)

    def test_should_not_contain_organization_active_date_out_of_31_days(self):
        organizations = get_expired_account_list()
        self.assertNotIn(self.expired_organization_out_of_31_days, organizations)

    def test_get_user_list_should_return_organization_creator(self):
        creators = get_creators([self.expired_organization_of_30_days])
        self.assertIn(self.user1, creators)

    def test_create_email_should_get_email_with_html_content(self):
        msg1 = create_email(self.user1)
        msg2 = create_email(self.user2)
        self.assertEqual(msg1.content_subtype,'html')
        self.assertEqual(msg2.content_subtype,'html')

    def test_create_email_should_get_email_with_right_subject(self):
        msg1 = create_email(self.user1)
        msg2 = create_email(self.user2)
        self.assertEqual(msg1.subject,'Please activate account email')
        self.assertEqual(msg2.subject,'Please activate account email')

    def test_create_email_should_get_email_contain_right_user_name(self):
        msg1 = create_email(self.user1)
        msg2 = create_email(self.user2)
        self.assertIn(self.user1.first_name+' '+self.user1.last_name ,msg1.body)
        self.assertIn(self.user2.first_name+' '+self.user2.last_name ,msg2.body)

    def test_create_email_should_get_right_recipient(self):
        msg1 = create_email(self.user1)
        msg2 = create_email(self.user2)
        self.assertIn(self.user1.email,msg1.to)
        self.assertIn(self.user2.email,msg2.to)

    def test_should_send_email_correct_times(self):
        organizations = get_expired_account_list()
        users = get_creators(organizations)

        with patch.object(EmailMessage, 'send') as send:
            send.return_value = True
            send_email(users)
            self.assertGreaterEqual(send.call_count, 1)

    def test_deactivate_email_sent(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        settings.EMAIL_FILE_PATH = 'email'
        send_deactivate_email()
        list = dircache.listdir('email')
        emails = ''
        for email in list:
            emails += open('email/'+email, 'r').read()
            os.remove('email/'+email)
        self.assertIn('From: ' + settings.EMAIL_HOST_USER, emails)
        self.assertIn('To: expired1@mail.com', emails)
        self.assertIn('Subject: Please activate account email', emails)
        self.assertIn('Hello first_name1 last_name1', emails)
        self.assertNotIn('To: expired2@mail.com', emails)
