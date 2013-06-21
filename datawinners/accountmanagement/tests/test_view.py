import unittest
from django.contrib.auth.models import User
from datawinners.accountmanagement.views import user_activity_log_details

class TestUserActivityLogDetails(unittest.TestCase):
    def test_should_render_user_activity_log_details_when_deleting_multiple_users(self):
        user_a = User(first_name="firstA", last_name="lastA", email="emailA")
        user_b = User(first_name="firstB", last_name="lastB", email="emailB")
        result = user_activity_log_details([user_a, user_b])

        self.assertEqual("Name: firstA lastA<br>Email: emailA<br><br>Name: firstB lastB<br>Email: emailB", result)
