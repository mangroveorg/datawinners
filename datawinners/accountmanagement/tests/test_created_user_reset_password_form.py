# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import unittest
from datawinners.accountmanagement.forms import CreatedUserPasswordResetForm
from mock import Mock, patch
from django.core.mail.backends.locmem import EmailBackend
from datawinners.utils import _get_email_template_name_for_created_user
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from datawinners.tests.test_email_utils import set_email_settings

class TestCreatedUserResetPasswordForm(unittest.TestCase):

    def setUp(self):
        set_email_settings()
        self.email_test = "test@mailinator.com"
        patch_clean_email = patch("django.contrib.auth.forms.PasswordResetForm.clean_email")
        self.mock_clean_email = patch_clean_email.start()
        patch_token_generator = patch("django.contrib.auth.tokens.default_token_generator.make_token")
        self.mock_token_generator = patch_token_generator.start()
        request = Mock()
        request.user.first_name = "rakoto"
        request.LANGUAGE_CODE = "en"
        self.request = request
        user = Mock(spec=User)
        user.email = self.email_test
        user.id = 1
        self.mock_user = user



    def send_messages_mock(self, email_messages):
        return email_messages
        

    def test_send_mail_to_newly_created_user(self):
        self.mock_clean_email.return_value = self.email_test
        self.mock_token_generator.return_value = "token4321"
        with patch.object(EmailBackend, "send_messages", self.send_messages_mock):
            reset_form = CreatedUserPasswordResetForm({"email": self.email_test})
            reset_form.users_cache = [self.mock_user]
            self.assertTrue(reset_form.is_valid())
            a = reset_form.save(email_template_name=_get_email_template_name_for_created_user(self.request.LANGUAGE_CODE),
                                    request=self.request)
            expected = u'<html>\n\n<body>\n\n<p>Hello ,</p>\n\n<p> has created a <a href="https://www.datawinners.com/">DataWinners</a> account for you.<br/>\n<a href="http://localhost:8000/password/reset/confirm/1-token4321/">Reset</a>\n your password to get started. Use your email to <a href="http://localhost:8000/login/">log in</a>\n once your password reset.\n</p>\n\n\n<p>\n<b>How to Create Project</b><br/>\nOn the Dashboard page, click on &laquo;Create a new Project&raquo; to create your Questionnaire. Once you have created your project,\nyou can register all the people who send you data (we call them Data Senders).\n</p>\n\n<p>\n<b>How to Collect Data</b><br/>\n<a href="https://www.datawinners.com/">DataWinners</a> allows you to collect your data in 3 diffrent ways, Choose the\nchannel most convenient for you and your Data Senders.\n    <ol>\n        <li><b>Web:</b> Collect an unlimited amount of data using the online Questionnaire.</li>\n        <li><b>Android Smartphone:</b> Download the Questionnaires directly onto your Android Smartphone.</li>\n        <li><b>SMS:</b> Use any simple mobile phone to send in data using a signle SMS.\n            <a href="https://www.datawinners.com/">Datawinners</a> will send automatic confirmation and error messages\n            back in response to your SMS.</li>\n    </ol>\n</p>\n\n<p><b>Need Help?</b><br>\n    If you need help getting started, check out our <a href=\'http:///en/support/find-answers/\' style="text-decoration: none">FAQs</a> and other online\n    <a href="http:///en/support/" style="text-decoration: none">support</a>. <br>\n    We can also be reach via Email at support@datawinners.com. We\'re here to help!\n</p>\n\n<p><b>Stay Connected</b><br>\n    We\'d love to hear from you! You can follow us on <a href="https://twitter.com/#!/datawinners" style="text-decoration: none">Twitter</a>, post on\n    our <a href="http://www.facebook.com/DataWinners" style="text-decoration: none">Facebook</a> wall and comment on our\n    <a href="http://datawinners.wordpress.com/" style="text-decoration: none">blog</a>. The blog is a great way to learn about new features and\n    upcoming DataWinners events.\n</p>\n\n<p>Have fun, <br>\n    Your DataWinners Team <br>\n    <a href="http://www.datawinners.com" style="text-decoration: none">www.datawinners.com</a> |\n    <a href="http://datawinners.wordpress.com/" style="text-decoration: none">Blog</a> |\n    <a href="https://twitter.com/#!/datawinners" style="text-decoration: none">Twitter</a>\n</p>\n\n</body>\n</html>'
            self.assertEqual(a[0].body, expected)


