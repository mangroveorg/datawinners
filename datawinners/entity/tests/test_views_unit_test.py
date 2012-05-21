from unittest.case import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, get_current_site
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from mock import  Mock, patch
from accountmanagement.models import Organization, NGOUserProfile
from accountmanagement.organization_id_creator import OrganizationIdCreator
from entity.views import send_activation_email_for_data_sender, create_single_web_user
from django.core import mail
from tests.test_email_utils import set_email_settings

WEB_USER_TEST_EMAIL = "test_email_for_create_single_web_user@test.com"


class TestView(TestCase):
    def prepare_organization(self):
        self.organization = Organization(name='test_org_for_paid_account',
            sector = 'PublicHealth', address = 'add',
            city = 'Pune', country = 'India',
            zipcode = '411006', in_trial_mode = False,
            org_id = OrganizationIdCreator().generateId())

        self.organization.save()

    def setUp(self):
        set_email_settings()
        self.prepare_organization()
        User.objects.filter(email = WEB_USER_TEST_EMAIL).delete()

    def tearDown(self):
        users = User.objects.filter(email = WEB_USER_TEST_EMAIL)
        NGOUserProfile.objects.filter(org_id = self.organization.org_id).delete()
        users.delete()
        Organization.objects.filter(name = 'test_org_for_paid_account').delete()

    def test_create_single_web_user(self):
        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            create_single_web_user(self.organization.org_id, WEB_USER_TEST_EMAIL, "test","en")
            user = User.objects.filter(email = WEB_USER_TEST_EMAIL)[0]
            emails = [mail.outbox.pop() for i in range(len(mail.outbox))]

            self.assertEqual(1, len(emails))
            sent_email = emails[0]

            self.assertEqual(settings.EMAIL_HOST_USER, sent_email.from_email)
            self.assertEqual([WEB_USER_TEST_EMAIL], sent_email.to)
            ctx_dict = {
                'domain': "localhost:8000",
                'uid': int_to_base36(user.id),
                'user': user,
                'token': "token",
                'protocol': 'http',
                }
            self.assertEqual(render_to_string('registration/password_reset_email_en.html', ctx_dict), sent_email.body)


    def test_should_send_correct_email_in_html_format_in_english(self):
        site = get_current_site(None)
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "en"
        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_activation_email_for_data_sender(user, language_code)
            emails = [mail.outbox.pop() for i in range(len(mail.outbox))]

            self.assertEqual(1, len(emails))
            sent_email = emails[0]

            self.assertEqual("html", sent_email.content_subtype)
            self.assertEqual(settings.EMAIL_HOST_USER, sent_email.from_email)
            self.assertEqual(['test@mail.com'], sent_email.to)
            self.assertEqual([settings.HNI_SUPPORT_EMAIL_ID], sent_email.bcc)
            ctx_dict = {
                'domain': site.domain,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': "token",
                'protocol': 'http',
                }
            self.assertEqual(render_to_string('email/activation_email_subject_for_data_sender_account_en.txt'), sent_email.subject)
            self.assertEqual(render_to_string('email/activation_email_for_data_sender_account_en.html', ctx_dict), sent_email.body)

    def test_should_send_correct_email_in_html_format_in_french(self):
        site = get_current_site(None)
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "fr"
        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_activation_email_for_data_sender(user, language_code)
            emails = [mail.outbox.pop() for i in range(len(mail.outbox))]

            self.assertEqual(1, len(emails))
            sent_email = emails[0]

            self.assertEqual("html", sent_email.content_subtype)
            self.assertEqual(settings.EMAIL_HOST_USER, sent_email.from_email)
            self.assertEqual(['test@mail.com'], sent_email.to)
            self.assertEqual([settings.HNI_SUPPORT_EMAIL_ID], sent_email.bcc)
            ctx_dict = {
                'domain': site.domain,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': "token",
                'protocol': 'http',
                }
            self.assertEqual(render_to_string('email/activation_email_subject_for_data_sender_account_fr.txt'), sent_email.subject)
            self.assertEqual(render_to_string('email/activation_email_for_data_sender_account_fr.html', ctx_dict), sent_email.body)
