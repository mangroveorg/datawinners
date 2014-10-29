# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date, datetime
import unittest
from mock import Mock, MagicMock
from datawinners.project.models import Reminder, ReminderMode, RemindTo, ReminderLog
from mangrove.datastore.database import DatabaseManager
from datawinners.project.forms import ReminderForm
from decimal import Decimal
from mangrove.form_model.deadline import Deadline, Week
from mangrove.form_model.project import Project


class TestReminders(unittest.TestCase):
    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_deadline(self):
        # same week
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(7),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_following_deadline(self):
        # same week
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(7),mode="Following")
        self.assertTrue(reminder.should_be_send_on(deadline, today))


    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_four_days_before_deadline(self):
        # Case where deadline is in next week, but reminder is scheduled today
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=4)
        deadline = Deadline(frequency=Week(2),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_on_weekend(self):
        # Case where deadline is in next week, but reminder is scheduled today
        today = date(2011, 9, 11)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(2),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))


    def test_should_return_false_for_reminder_before_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 9, 9)
        # Sunday deadline
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=1)
        deadline = Deadline(frequency=Week(7),mode="That")
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_after_deadline_type_if_today_is_two_days_after_deadline(self):
        #  same week
        today = date(2011, 9, 10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(4),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    #    2
    def test_should_return_true_for_reminder_after_deadline_type_if_today_is_three_days_after_deadline_2(self):
        # next week
        today = date(2011, 9,13 )
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=3)
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))


    def test_should_return_false_for_reminder_after_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 9, 10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=1)
        deadline = Deadline(frequency=Week(4),mode="That")
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_on_deadline_type_if_today_is_on_deadline(self):
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Deadline(frequency=Week(5),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_false_for_reminder_on_deadline_type_if_today_is_not_on_deadline(self):
        today = date(2011, 9, 10)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Deadline(frequency=Week(5),mode="That")
        self.assertFalse(reminder.should_be_send_on(deadline, today))


    def test_should_return_all_data_senders_as_sender_list_if_remind_to_mode_is_all_datasenders(self):
        data_senders = [{'name': 'reporter1', 'mobile_number': 'tel1'},
                {'name': 'reporter2', 'mobile_number': 'tel2'},
                {'name': 'reporter3', 'mobile_number': 'tel3'},
                {'name': 'reporter4', 'mobile_number': 'tel4'}
        ]
        today = date(2011, 2, 10)
        project = MagicMock(spec=Project)
        project.get_data_senders.return_value = data_senders
        project.reminder_and_deadline.return_value = dict(should_send_reminder_to_all_ds=True)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        self.assertEqual(data_senders, reminder.get_sender_list(project, today,None))


    def test_should_return_data_senders_as_sender_list_if_remind_to_mode_is_datasenders_without_submissions(self):

        reminder_and_deadline_dict = {'should_send_reminder_to_all_ds': False}

        def getitem(name):
            return reminder_and_deadline_dict[name]

        data_senders = [{'name': 'reporter1', 'mobile_number': 'tel1'},
                {'name': 'reporter2', 'mobile_number': 'tel2'},
                {'name': 'reporter3', 'mobile_number': 'tel3'},
                {'name': 'reporter4', 'mobile_number': 'tel4'}
        ]
        today = date(2011, 2, 10)
        project = MagicMock(spec=Project)
        expected_sender_list = [data_senders[0], data_senders[2]]
        project.get_data_senders_without_submissions_for.return_value = expected_sender_list
        project.reminder_and_deadline.__getitem__.side_effect = getitem
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        self.assertEqual(expected_sender_list, reminder.get_sender_list(project, today,None))


    def test_should_calculate_frequency_period_for_next_deadline_if_reminder_on_deadline(self):
        today = date(2011, 2, 10)
        project = MagicMock(spec=Project)
        mock_deadline = MagicMock(spec=Deadline)
        project.deadline.return_value = mock_deadline
        reminder_and_deadline_dict = {'should_send_reminder_to_all_ds': False}

        def getitem(name):
            return reminder_and_deadline_dict[name]
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        project.reminder_and_deadline.__getitem__.side_effect = getitem
        reminder.get_sender_list(project, today,None)
        mock_deadline.current_deadline.assert_called_once_with(today)

    def test_should_calculate_frequency_period_for_next_deadline_if_reminder_before_deadline(self):
        reminder_and_deadline_dict = {'should_send_reminder_to_all_ds': False}
        def getitem(name):
            return reminder_and_deadline_dict[name]
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE)
        today = date(2011, 2, 10)
        project = MagicMock(spec=Project)
        mock_deadline = MagicMock(spec=Deadline)
        project.deadline.return_value = mock_deadline
        project.reminder_and_deadline.__getitem__.side_effect = getitem
        reminder.get_sender_list(project, today,None)
        mock_deadline.next_deadline.assert_called_once_with(today)


    def test_should_calculate_frequency_period_for_current_deadline_if_reminder_after_deadline(self):
        reminder_and_deadline_dict = {'should_send_reminder_to_all_ds': False, 'has_deadline': True}
        def getitem(name):
            return reminder_and_deadline_dict[name]
        today = date(2011, 2, 10)
        project = MagicMock(spec=Project)
        mock_deadline = MagicMock(spec=Deadline)
        project.deadline.return_value = mock_deadline
        project.reminder_and_deadline.__getitem__.side_effect = getitem
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE)
        reminder.get_sender_list(project, today, None)
        mock_deadline.current_deadline.assert_called_once_with(today)


    def test_should_create_reminder_log(self):
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=2)
        dbm_mock = Mock(spec=DatabaseManager)
        log = reminder.log(dbm_mock, 'test_project', datetime.now(),to_number = 'ads', number_of_sms=10)
        self.assertTrue(isinstance(log, ReminderLog))
        dbm_mock._save_document.assert_called_once()


class TestReminderForm(unittest.TestCase):

    def test_should_give_error_if_before_deadline_field_is_blank(self):
        data = {
            'should_send_reminders_before_deadline':True,
            'number_of_days_before_deadline':'',
            'reminder_text_before_deadline':''
        }
        form = ReminderForm(data)
        self.assertFalse(form.is_valid())
        error_message = {
            'number_of_days_before_deadline':[u'This field is required'],
            'reminder_text_before_deadline':[u'This field is required']
        }
        self.assertEqual(error_message,form.errors)

    def test_should_not_give_error_if_before_deadline_is_not_checked(self):
        data = {
            'should_send_reminders_before_deadline':False,
            'number_of_days_before_deadline':'1',
            'reminder_text_before_deadline':'1 day left'
        }
        form = ReminderForm(data)
        self.assertTrue(form.is_valid())
        cleaned_data_value = {
            'deadline_week': u'',
            'deadline_type_week': u'',
            'deadline_month': u'',
            'deadline_type_month': u'',
            'deadline_type': u'',
            'frequency_period': u'',
            'should_send_reminders_before_deadline':False,
            'number_of_days_before_deadline':Decimal('1'),
            'reminder_text_before_deadline':u'1 day left',
            'should_send_reminders_on_deadline':False,
            'reminder_text_on_deadline':u'',
            'should_send_reminders_after_deadline':False,
            'number_of_days_after_deadline':None,
            'reminder_text_after_deadline':u'',
            'whom_to_send_message': False
        }
        self.assertEqual(cleaned_data_value,form.cleaned_data)

    def test_should_give_error_if_on_deadline_field_is_blank(self):
        data = {
            'should_send_reminders_on_deadline':True,
            'reminder_text_on_deadline':''
        }
        form = ReminderForm(data)
        self.assertFalse(form.is_valid())
        error_message = {
            'reminder_text_on_deadline':[u'This field is required']
        }
        self.assertEqual(error_message,form.errors)

    def test_should_not_give_error_if_on_deadline_is_not_checked(self):
        data = {
            'should_send_reminders_on_deadline':False,
            'reminder_text_on_deadline':'1 day left'
        }
        form = ReminderForm(data)
        self.assertTrue(form.is_valid())
        cleaned_data_value = {
            'deadline_week': u'',
            'deadline_type_week': u'',
            'deadline_month': u'',
            'deadline_type_month': u'',
            'deadline_type': u'',
            'frequency_period': u'',
            'should_send_reminders_before_deadline':False,
            'number_of_days_before_deadline':None,
            'reminder_text_before_deadline':u'',
            'should_send_reminders_on_deadline':False,
            'reminder_text_on_deadline':u'1 day left',
            'should_send_reminders_after_deadline':False,
            'number_of_days_after_deadline':None,
            'reminder_text_after_deadline':u'',
            'whom_to_send_message': False
        }
        self.assertEqual(cleaned_data_value,form.cleaned_data)

    def test_should_give_error_if_after_deadline_field_is_blank(self):
        data = {
            'should_send_reminders_after_deadline':True,
            'number_of_days_after_deadline':'',
            'reminder_text_after_deadline':''
        }
        form = ReminderForm(data)
        self.assertFalse(form.is_valid())
        error_message = {
            'number_of_days_after_deadline':[u'This field is required'],
            'reminder_text_after_deadline':[u'This field is required']
        }
        self.assertEqual(error_message,form.errors)

    def test_should_not_give_error_if_after_deadline_is_not_checked(self):
        data = {
            'should_send_reminders_after_deadline':False,
            'number_of_days_after_deadline':'1',
            'reminder_text_after_deadline':'1 day left'
        }
        form = ReminderForm(data)
        self.assertTrue(form.is_valid())
        cleaned_data_value = {
            'deadline_week': u'',
            'deadline_type_week': u'',
            'deadline_month': u'',
            'deadline_type_month': u'',
            'deadline_type': u'',
            'frequency_period': u'',
            'should_send_reminders_before_deadline':False,
            'number_of_days_before_deadline':None,
            'reminder_text_before_deadline':u'',
            'should_send_reminders_on_deadline':False,
            'reminder_text_on_deadline':u'',
            'should_send_reminders_after_deadline':False,
            'number_of_days_after_deadline':Decimal('1'),
            'reminder_text_after_deadline':u'1 day left',
            'whom_to_send_message': False
        }
        self.assertEqual(cleaned_data_value,form.cleaned_data)
