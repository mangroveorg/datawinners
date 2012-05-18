from unittest.case import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.http import int_to_base36
from mock import  Mock, patch
from entity.views import send_activation_email_for_data_sender
from django.core import mail


class TestView(TestCase):

    def test_should_send_correct_email(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        site = Site(domain='test', name='test_site')
        user = Mock(spec=User)
        user.email = 'test@mail.com'
        user.id = 1
        user.first_name = "test"
        language_code = "en"
        with patch("django.contrib.auth.tokens.default_token_generator.make_token") as make_token:
            make_token.return_value = "token"
            send_activation_email_for_data_sender(site, user, language_code)
            emails = [mail.outbox.pop() for i in range(len(mail.outbox))]

            self.assertEqual(1, len(emails))
            sent_email = emails[0]

            self.assertEqual("html", sent_email.content_subtype)
            self.assertEqual(settings.EMAIL_HOST_USER, sent_email.from_email)
            self.assertEqual(['test@mail.com'], sent_email.to)
            self.assertEqual([settings.HNI_SUPPORT_EMAIL_ID], sent_email.bcc)
            ctx_dict = {
                'domain': "test",
                'uid': int_to_base36(user.id),
                'username': user.first_name,
                'token': "token",
                'protocol': 'http',
                }
            self.assertEqual(render_to_string('email/activation_email_subject_for_data_sender_account_en.txt'), sent_email.subject)
            self.assertEqual(render_to_string('email/activation_email_for_data_sender_account_en.html', ctx_dict), sent_email.body)
