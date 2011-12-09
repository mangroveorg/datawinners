# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.models import User
from django.utils import unittest
import os
from registration.models import RegistrationProfile
from datawinners.accountmanagement.models import Organization, NGOUserProfile, PaymentDetails
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator
from datawinners.accountmanagement.registration_processors import get_registration_processor, PaidAccountRegistrationProcessor, TrialAccountRegistrationProcessor
from django.contrib.sites.models import Site
import dircache
from django.conf import settings
from mangrove.utils.types import is_not_empty


class TestRegistrationProcessor(unittest.TestCase):
    def prepare_organization(self):
        self.paid_organization = Organization(name='test_org_for_paid_account',
                                              sector='PublicHealth', address='add',
                                              city='Pune', country='India',
                                              zipcode='411006', in_trial_mode=False,
                                              org_id=OrganizationIdCreator().generateId())
        
        self.trial_organization = Organization(name='test_org_for_trial_account',
                                                            sector='PublicHealth', address='add',
                                                            city='Pune', country='India',
                                                            zipcode='411006', in_trial_mode=True,
                                                            org_id=OrganizationIdCreator().generateId())
        self.paid_organization.save()
        self.trial_organization.save()

    def setUp(self):
        User.objects.filter(username = 'paid_account@mail.com').delete()
        User.objects.filter(username = 'trial_account@mail.com').delete()
        Organization.objects.filter(name='test_org_for_paid_account').delete()
        Organization.objects.filter(name='test_org_for_trial_account').delete()

        self.user1 = RegistrationProfile.objects.create_inactive_user(username='paid_account@mail.com', email='paid_account@mail.com', password='hi', site=Site(), send_email=False)
        self.user2 = RegistrationProfile.objects.create_inactive_user(username='trial_account@mail.com', email='trial_account@mail.com', password='hi', site=Site(), send_email=False)

        self.user1.first_name = 'first_name1'
        self.user1.last_name = 'last_name1'

        self.user2.first_name = 'first_name2'
        self.user2.last_name = 'last_name2'

        self.user1.save()
        self.user2.save()

        self.prepare_organization()

        NGOUserProfile(user = self.user1,title = 'Mr.',org_id = self.paid_organization.org_id).save()
        NGOUserProfile(user = self.user2,title = 'Ms.',org_id = self.trial_organization.org_id).save()


    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.paid_organization.delete()
        self.trial_organization.delete()


    def test_should_get_the_correct_registration_processor(self):
        self.assertTrue(isinstance(get_registration_processor(self.trial_organization), TrialAccountRegistrationProcessor))

        self.assertTrue(isinstance(get_registration_processor(self.paid_organization), PaidAccountRegistrationProcessor))

    def test_should_process_registration_data_for_paid_acccount(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        settings.EMAIL_FILE_PATH = '/tmp/email'

        processor = get_registration_processor(self.paid_organization)

        site = Site(domain='test', name='test_site')
        kwargs = dict(invoice_period='', preferred_payment='')

        processor.process(self.user1, site, kwargs)

        file_list = dircache.listdir('/tmp/email')
        emails = [self.xyz(single_file, '/tmp/email/') for single_file in file_list]
        self.assertEqual(1, len(emails))
        email = emails[0]
        self.assertIn('Content-Type: text/html', email)
        self.assertIn('From: ' + settings.EMAIL_HOST_USER, email)
        self.assertIn('To: paid_account@mail.com', email)
        self.assertIn('Subject: Account activation on test_site', email)
        self.assertIn('Hello first_name1 last_name1,', email)
        activation_link = 'http://test/activate/'+ (RegistrationProfile.objects.get(user=self.user1)).activation_key + '/'
        self.assertIn(activation_link, email)
        self.assertTrue(is_not_empty(PaymentDetails.objects.filter(organization=self.paid_organization)))

    def test_should_process_registration_data_for_trial_acccount(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        settings.EMAIL_FILE_PATH = '/tmp/email1'


        processor = get_registration_processor(self.trial_organization)

        site = Site(domain='test', name='test_site')
        kwargs = dict(invoice_period='', preferred_payment='')

        processor.process(self.user2, site, kwargs)

        file_list = dircache.listdir('/tmp/email1')
        emails = [self.xyz(single_file, '/tmp/email1/') for single_file in file_list]

        self.assertEqual(1, len(emails))
        email = emails[0]
        self.assertIn('From: ' + settings.EMAIL_HOST_USER, email)
        self.assertIn('To: trial_account@mail.com', email)
        self.assertIn('Subject: DataWinners Trial Account Activation', email)
        self.assertIn('Hello first_name2 last_name2,', email)
        activation_link = 'http://test/activate/'+ (RegistrationProfile.objects.get(user=self.user2)).activation_key + '/'
        self.assertIn(activation_link, email)

    def xyz(self, single_file, email_folder):
       email =  open(email_folder + single_file, 'r').read()
       os.remove(email_folder + single_file)
       return email