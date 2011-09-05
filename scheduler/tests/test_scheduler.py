from django.utils import unittest
from datawinners.scheduler.scheduler import send_reminders

class TestScheduler(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_should_send_reminder_when_frequency_is_on_deadline(self):
        reminder_and_deadline_for_month = {
            "reminders_enabled": "True",
            "deadline_month": "5",
            "deadline_type": "current",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "month"
        }
        project_reminders = Project(name="ReminderProject", reminder_and_deadline=reminder_and_deadline_for_month)
        send_reminders()

    def test_should_send_reminder_when_frequency_is_on_deadline(self):
        send_reminders()

    def test_should_send_reminder_when_frequency_is_on_deadline(self):
        send_reminders()