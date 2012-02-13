# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from django.core.urlresolvers import reverse
from mock import Mock
from datawinners.project.models import Reminder, RemindTo, ReminderMode, Project
from datawinners.project.views import _format_reminders, subject_registration_form_preview, registered_subjects, edit_subject, create_datasender, registered_datasenders, make_data_sender_links, add_link, all_datasenders
from datawinners.project.views import make_subject_links, subjects

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

        reminders = [reminder1, reminder2]
        formated_reminders = _format_reminders(reminders, 'test_project')

        self.assertEqual(2, len(formated_reminders))
        self.assertEqual('/project/delete_reminder/test_project/1/', formated_reminders[0]['delete_link'])

        self.assertEqual('On Deadline', formated_reminders[0]['when'])
        self.assertEqual('Datasenders Without Submissions', formated_reminders[0]['to'])

        self.assertEqual('2 days Before Deadline', formated_reminders[1]['when'])
        self.assertEqual('All Datasenders', formated_reminders[1]['to'])

    def test_should_return_subject_project_links(self):
        project = Mock(spec=Project)
        project_id = "1"
        project.id = project_id
        subject_links = make_subject_links(project)
        self.assertEqual(reverse(subjects, args=[project_id]), subject_links['subjects_link'])
        self.assertEqual(reverse(edit_subject, args=[project_id]), subject_links['subjects_edit_link'])
        self.assertEqual(reverse(subject_registration_form_preview, args=[project_id]),
            subject_links['subject_registration_preview_link'])
        self.assertEqual(reverse(registered_subjects, args=[project_id]), subject_links['registered_subjects_link'])
        self.assertEqual(reverse('subject_questionnaire', args=[project_id]), subject_links['register_subjects_link'])

    def test_should_return_datasender_project_links(self):
        project = Mock(spec=Project)
        project_id = "1"
        project.id = project_id
        datasender_links = make_data_sender_links(project)
        self.assertEqual(reverse(all_datasenders), datasender_links['datasenders_link'])
        self.assertEqual(reverse(create_datasender, args=[project_id]), datasender_links['register_datasenders_link'])
        self.assertEqual(reverse(registered_datasenders, args=[project_id]),
            datasender_links['registered_datasenders_link'])


    def test_for_websubmission_on_subjects_should_provide_add_links(self):
        project = Mock(spec=Project)
        project.id = "1"
        project.entity_type = "clinic"
        link = add_link(project)
        self.assertEqual(reverse('subject_questionnaire', args=[project.id]), link.url)
        self.assertEqual('Register a clinic', link.text)

    def test_for_websubmission_on_datasenders_should_provide_add_links(self):
        project = Mock(spec=Project)
        project.id = "1"
        project.entity_type = "reporter"
        link = add_link(project)
        self.assertEqual(reverse(create_datasender, args=[project.id]), link.url)
        self.assertEqual('Add a datasender', link.text)

  