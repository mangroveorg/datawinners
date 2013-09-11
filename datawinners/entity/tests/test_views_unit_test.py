from unittest.case import TestCase

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from mock import Mock, patch, PropertyMock
from django.core import mail

from datawinners.entity.views import initialize_values
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.entity.views import create_single_web_user
from datawinners.entity.import_data import send_email_to_data_sender
from datawinners.tests.email_utils import set_email_settings
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel


WEB_USER_TEST_EMAIL = "test_email_for_create_single_web_user@test.com"


class TestView(TestCase):
    def setUp(self):
        set_email_settings()

    def test_create_single_web_user(self):
        org = Mock(spec=Organization)
        org.org_id = "org_id"

        mock_entity = Mock(spec=Entity)
        mock_entity.value.return_value = 'test'

        users = User.objects.filter(email=WEB_USER_TEST_EMAIL)
        NGOUserProfile.objects.filter(org_id=org.org_id).delete()
        users.delete()

        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            with patch("datawinners.entity.views.get_database_manager_for_org") as get_dbm:
                get_dbm.return_value = Mock(spec=DatabaseManager)
                with patch("datawinners.accountmanagement.models.Organization.objects.get") as get_organization_mock:
                    get_organization_mock.return_value = org
                    with patch("datawinners.entity.views.get_by_short_code") as reporter_entity:
                        reporter_entity.return_value = mock_entity
                        create_single_web_user(org.org_id, WEB_USER_TEST_EMAIL, "test", "en")
                        user = User.objects.filter(email=WEB_USER_TEST_EMAIL)[0]
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
                        self.assertEqual(render_to_string(
                            'activatedatasenderemail/activation_email_subject_for_data_sender_account_en.txt'),
                                         sent_email.subject)
                        self.assertEqual(
                            render_to_string('activatedatasenderemail/activation_email_for_data_sender_account_en.html',
                                             ctx_dict), sent_email.body)


    def test_should_send_correct_activation_email_in_html_format_in_english(self):
        site = get_current_site(None)
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "en"
        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_email_to_data_sender(user, language_code)
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
            self.assertEqual(
                render_to_string('activatedatasenderemail/activation_email_subject_for_data_sender_account_en.txt'),
                sent_email.subject)
            self.assertEqual(
                render_to_string('activatedatasenderemail/activation_email_for_data_sender_account_en.html', ctx_dict),
                sent_email.body)

    def test_should_send_correct_activaton_email_in_html_format_in_french(self):
        site = get_current_site(None)
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "fr"
        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_email_to_data_sender(user, language_code)
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
            self.assertEqual(
                render_to_string('activatedatasenderemail/activation_email_subject_for_data_sender_account_fr.txt'),
                sent_email.subject)
            self.assertEqual(
                render_to_string('activatedatasenderemail/activation_email_for_data_sender_account_fr.html', ctx_dict),
                sent_email.body)


    def test_should_send_correct_email_in_html_format_in_french_to_a_newly_created_user(self):
        site = get_current_site(None)
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "fr"

        request = Mock()
        request.user.first_name = "rakoto"

        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_email_to_data_sender(user, language_code, type="created_user", request=request)
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
                'creator_user': request.user.first_name,
                'site': site,
            }
            self.assertEqual(render_to_string('registration/created_user_email_subject_fr.txt') % site.domain,
                             sent_email.subject)
            self.assertEqual(render_to_string('registration/created_user_email_fr.html', ctx_dict), sent_email.body)

    def test_should_send_correct_email_in_html_format_in_english_to_a_newly_created_user(self):
        site = get_current_site(None)
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "en"

        request = Mock()
        request.user.first_name = "rakoto"

        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_email_to_data_sender(user, language_code, type="created_user", request=request)
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
                'creator_user': request.user.first_name,
                'site': site,
            }
            self.assertEqual(render_to_string('registration/created_user_email_subject_en.txt') % site.domain,
                             sent_email.subject)
            self.assertEqual(render_to_string('registration/created_user_email_en.html', ctx_dict), sent_email.body)


    def test_should_set_field_initial_value_as_none_if_not_populated(self):
        empty_field = TextField(name="text", code="code", label="what is ur name", ddtype=Mock)
        empty_field.value = None
        form_model = FormModel(Mock(spec=DatabaseManager))
        form_model.add_field(empty_field)

        mock_subject = Mock(spec=Entity)
        type(mock_subject).data = PropertyMock(return_value={})

        initialize_values(form_model, mock_subject)

        self.assertEquals(None, empty_field.value)

    def test_should_convert_field_value_to_unicode_when_field_value_present(self):
        empty_field = TextField(name="text", code="code", label="what is ur name", ddtype=Mock)
        empty_field.value = "FirstName"
        form_model = FormModel(Mock(spec=DatabaseManager))
        form_model.add_field(empty_field)

        mock_subject = Mock(spec=Entity)
        type(mock_subject).data = PropertyMock(return_value={"text": {"value": "SomeValue"}})

        initialize_values(form_model, mock_subject)

        self.assertIsInstance(empty_field.value, unicode)
        self.assertEquals(u"SomeValue", empty_field.value)

