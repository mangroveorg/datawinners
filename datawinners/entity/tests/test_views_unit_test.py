from collections import OrderedDict
import json
from unittest.case import TestCase

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from mock import Mock, patch, PropertyMock, MagicMock
from django.core import mail
from datawinners.entity.view.unique_id import _subject_short_codes_to_delete

from datawinners.entity.views import initialize_values, _set_contacts_email_address, create_multiple_web_users, \
    _set_email_for_contacts
from datawinners.entity.views import _format_imported_subjects_datetime_field_to_str
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity, Contact
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.entity.views import create_single_web_user
from datawinners.entity.import_data import send_email_to_data_sender
from datawinners.search.entity_search import SubjectQuery
from datawinners.tests.email_utils import set_email_settings
from mangrove.form_model.field import TextField, DateField
from mangrove.form_model.form_model import FormModel
import datetime


WEB_USER_TEST_EMAIL = "test_email_for_create_single_web_user@test.com"


class TestView(TestCase):
    def setUp(self):
        set_email_settings()

    def test_create_single_web_user(self):
        org = Mock(spec=Organization)
        org.org_id = "org_id"
        org.account_type = "Basic"
        site = get_current_site(None)

        mock_entity = Mock(spec=Contact)
        mock_entity.value.return_value = 'test'

        users = User.objects.filter(email=WEB_USER_TEST_EMAIL)
        NGOUserProfile.objects.filter(org_id=org.org_id).delete()
        users.delete()

        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            with patch("datawinners.accountmanagement.helper.get_database_manager_for_org") as get_dbm:
                get_dbm.return_value = Mock(spec=DatabaseManager)
                with patch("datawinners.accountmanagement.models.Organization.objects.get") as get_organization_mock:
                    get_organization_mock.return_value = org
                    with patch("datawinners.accountmanagement.helper.contact_by_short_code") as reporter_entity:
                        with patch(
                                "datawinners.accountmanagement.helper.set_email_for_contact") as set_email_for_contact_mock:
                            set_email_for_contact_mock.return_value = None
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
                                'account_type': org.account_type,
                                'site': site,
                            }
                            self.assertEqual(render_to_string(
                                'activatedatasenderemail/activation_email_subject_for_data_sender_account_en.txt'),
                                             sent_email.subject)
                            self.assertEqual(
                                render_to_string(
                                    'activatedatasenderemail/activation_email_for_data_sender_account_en.html',
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
                'site': site,
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
                'site': site,
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
                'account_type': 'Pro SMS',
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
                'account_type': 'Pro SMS',
            }
            self.assertEqual(render_to_string('registration/created_user_email_subject_en.txt') % site.domain,
                             sent_email.subject)
            self.assertEqual(render_to_string('registration/created_user_email_en.html', ctx_dict), sent_email.body)


    def test_should_set_field_initial_value_as_none_if_not_populated(self):
        empty_field = TextField(name="text", code="code", label="what is ur name")
        empty_field.value = None
        form_model = FormModel(Mock(spec=DatabaseManager))
        form_model.add_field(empty_field)

        mock_subject = Mock(spec=Entity)
        type(mock_subject).data = PropertyMock(return_value={})

        initialize_values(form_model, mock_subject)

        self.assertEquals(None, empty_field.value)

    def test_should_convert_field_value_to_unicode_when_field_value_present(self):
        empty_field = TextField(name="text", code="code", label="what is ur name")
        empty_field.value = "FirstName"
        form_model = FormModel(Mock(spec=DatabaseManager))
        form_model.add_field(empty_field)

        mock_subject = Mock(spec=Entity)
        type(mock_subject).data = PropertyMock(return_value={"text": {"value": "SomeValue"}})

        initialize_values(form_model, mock_subject)

        self.assertIsInstance(empty_field.value, unicode)
        self.assertEquals(u"SomeValue", empty_field.value)

    def test_select_short_codes_sent_from_web_when_all_ids_not_selected(self):
        request = HttpRequest()
        request.POST = {"all_ids": "1;2;3"}
        self.assertEquals(_subject_short_codes_to_delete(request, Mock(DatabaseManager), "test_type"), ['1', '2', '3'])

    def test_select_short_codes_using_search_query_when_all_selected_on_web(self):
        request = HttpRequest()
        request.user = 'test'
        request.POST = {"all_ids": "1;2;3", "all_selected": "true", "search_query": "something"}
        with patch("datawinners.entity.view.unique_id.SubjectQuery")  as mock_subject_query_class:
            with patch(
                    "datawinners.entity.view.unique_id.get_form_model_by_entity_type") as get_form_model_by_entity_type:
                with patch("datawinners.entity.view.unique_id.header_fields") as header_fields:
                    instance = Mock(spec=SubjectQuery)
                    mock_subject_query_class.return_value = instance
                    mock_form_model = Mock(FormModel)
                    get_form_model_by_entity_type.return_value = mock_form_model
                    instance.query.return_value = [['s', 'x'], ['s', 'y']]
                    header = OrderedDict()
                    header.update({"name": "name"})
                    header.update({"short_code": "unique id"})
                    header_fields.return_value = header
                    self.assertEquals(_subject_short_codes_to_delete(request, mock_form_model, "test_type"),
                                      ['x', 'y'])
                    instance.query.assert_called_once_with('test', 'test_type', 'something')
                    header_fields.assert_called_once_with(mock_form_model)


    def test_should_convert_datetime_to_string_after_subject_import(self):
        form_model = Mock(spec=FormModel)
        date_field = DateField('name', 'code', 'Date of birth', '')
        form_model.fields = [Mock(spec=TextField), date_field]
        subjects_data = {
            u'fac8': OrderedDict([('q2', u'Safidy'), ('q7', datetime.datetime(2010, 10, 10, 0, 0)), ('q6', u'fac8')]),
            u'fac9': OrderedDict([('q2', u'Emission'), ('q7', datetime.datetime(1947, 6, 26, 0, 0)), ('q6', u'fac9')]),
            u'fac7': OrderedDict([('q2', u'Patrick'), ('q7', datetime.datetime(2002, 3, 25, 0, 0)), ('q6', u'fac7')])}

        formated_data = _format_imported_subjects_datetime_field_to_str(form_model, subjects_data)
        expected_data = [[u'Safidy', '10-10-2010', u'fac8'], [u'Emission', '26-6-1947', u'fac9'],
                         [u'Patrick', '25-3-2002', u'fac7']]
        self.assertEqual(expected_data, formated_data)


class TestWebUserAccess(TestCase):

    def test_should_update_email_address_for_contact(self):
        dbm = Mock(spec=DatabaseManager)
        request = MagicMock()
        request.POST = {'post_data': json.dumps([{'email': 'contacts_email', 'reporter_id': 'rep_id'}])}
        contact = Mock(spec=Contact)
        contact.is_contact = True

        with patch('datawinners.entity.views.set_email_for_contact') as set_email_contact_mock:
            with patch('datawinners.entity.views.contact_by_short_code') as contact_by_short_code_mock:
                contact_by_short_code_mock.return_value = contact

                email_id_map = _set_contacts_email_address(dbm, request)

                set_email_contact_mock.assert_called_with(dbm, contact, 'contacts_email')

    def test_should_update_email_address_for_data_sender_and_send_mail(self):
        dbm = Mock(spec=DatabaseManager)
        request = MagicMock()
        request.POST = {'post_data': json.dumps([{'email': 'data_sender_email', 'reporter_id': 'rep_id'}])}
        request.method = 'POST'
        request.LANGUAGE_CODE = 'en'
        expected_contact_id_map = {'rep_id': 'data_sender_email'}
        contact = MagicMock(spec=Contact)
        contact.is_contact = False

        with patch('datawinners.entity.views.create_web_users') as create_web_users_mock:
            with patch('datawinners.entity.views.contact_by_short_code') as contact_by_short_code_mock:
                with patch('datawinners.entity.views.set_email_for_contact') as set_email_for_contact_mock:
                    contact_by_short_code_mock.return_value = contact

                    _set_email_for_contacts(dbm, 'org_id', request)

                    self.assertFalse(set_email_for_contact_mock.called)
                    create_web_users_mock.assert_called_with('org_id', expected_contact_id_map, 'en')

