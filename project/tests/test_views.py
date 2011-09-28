# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from mock import Mock
from datawinners.project.models import Reminder, RemindTo, ReminderMode
from datawinners.project.views import _format_reminders

class TestProjectViews(unittest.TestCase):

    def test_should_return_reminders_in_the_required_format(self):
        reminder1 = Mock(spec=Reminder)
        reminder1.message = ''
        reminder1.id = '1'
        reminder1.remind_to = RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS
        reminder1.reminder_mode = ReminderMode.ON_DEADLINE
        reminder1.day = 0

        reminder2 = Mock(spec=Reminder)
        reminder2.message = ''
        reminder2.id = '2'
        reminder2.remind_to = RemindTo.ALL_DATASENDERS
        reminder2.reminder_mode = ReminderMode.BEFORE_DEADLINE
        reminder2.day = 2

        reminders=[reminder1, reminder2]
        formated_reminders = _format_reminders(reminders, 'test_project')

        self.assertEqual(2,len(formated_reminders))
        self.assertEqual('/project/delete_reminder/test_project/1/',formated_reminders[0]['delete_link'])

        self.assertEqual('On Deadline',formated_reminders[0]['when'])
        self.assertEqual('Datasenders Without Submissions',formated_reminders[0]['to'])

        self.assertEqual('2 days Before Deadline',formated_reminders[1]['when'])
        self.assertEqual('All Datasenders',formated_reminders[1]['to'])


  