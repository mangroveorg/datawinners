# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.forms import Form
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import Mock, patch
from datawinners.project.models import Reminder, RemindTo, ReminderMode, Project
from datawinners.project.views import _format_reminders, subject_registration_form_preview, registered_subjects, edit_subject, create_datasender_and_webuser, registered_datasenders, make_data_sender_links, add_link, all_datasenders
from datawinners.project.views import make_subject_links, subjects
from project.models import ProjectState
from project.preview_views import get_sms_preview_context, get_questions, get_web_preview_context, add_link_context
from project.views import get_form_model_and_template
from project.wizard_view import get_preview_and_instruction_links

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
        self.assertEqual(reverse(create_datasender_and_webuser, args=[project_id]), datasender_links['register_datasenders_link'])
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
        self.assertEqual(reverse(create_datasender_and_webuser, args=[project.id]), link.url)
        self.assertEqual('Add a datasender', link.text)

    def test_should_get_correct_template_for_non_data_sender(self):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        project = Project(project_type = "survey", entity_type = "clinic", state = ProjectState.ACTIVE)

        with patch.object(FormModel, "get") as get_form_model:
            get_form_model.return_value = {}
            is_data_sender = False
            subject = False
            form_model, template = get_form_model_and_template(manager, project, is_data_sender, subject)
            self.assertEquals(template, "project/web_questionnaire.html")

    def test_should_get_correct_template_for_data_sender(self):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        project = Project(project_type = "survey", entity_type = "clinic", state = ProjectState.ACTIVE)

        with patch.object(FormModel, "get") as get_form_model:
            get_form_model.return_value = {}
            is_data_sender = True
            subject = False
            form_model, template = get_form_model_and_template(manager, project, is_data_sender, subject)
            self.assertEquals(template, "project/data_submission.html")

    def test_should_get_correct_template_for_subject_questionnaire(self):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        project = Project(project_type = "survey", entity_type = "clinic", state = ProjectState.ACTIVE)

        with patch.object(FormModel, "get") as get_form_model:
            get_form_model.return_value = {}
            with patch("project.views.get_form_model_by_entity_type") as get_subject_form:
                get_subject_form.return_value = {}
                is_data_sender = False
                subject = True
                form_model, template = get_form_model_and_template(manager, project, is_data_sender, subject)
                self.assertEquals(template, "project/register_subject.html")


    def test_should_get_preview_and_instruction_links(self):
        with patch("project.wizard_view.reverse") as reverse:
            reverse.side_effect = lambda *args, **kw: "/project/%s" % args[0]
            links = get_preview_and_instruction_links()
            self.assertEqual(links["sms_preview"], "/project/sms_preview")
            self.assertEqual(links["web_preview"], "/project/web_preview")

    def test_should_get_correct_context_for_sms_preview(self):
        questions = {}
        manager = {}
        project = {"name": "project_name", "entity_type":"clinic", "language":"en"}
        form_model = Mock()
        form_model.fields = [{}]
        form_model.form_code = "form code"
        project_form = Mock()
        project_form.cleaned_data = {
            "name":"project_name", "entity_type":"clinic", "language":"en"
        }

        post = {"questionnaire-code": "q01",
                "question-set": "",
                "profile_form": '{"name":"project_name", "entity_type":"clinic", "language":"en"}'}



        with patch("project.preview_views.get_all_entity_types") as entities:
            entities.return_value = {}
            with patch("project.preview_views.remove_reporter") as removed_entities:
                removed_entities.return_value = {}
                with patch("project.preview_views.CreateProject") as create_project:
                    create_project.return_value = project_form
                    with patch("project.preview_views.create_questionnaire") as questionnaire:
                        questionnaire.return_value = form_model
                        with patch("project.preview_views.get_questions") as get_questions:
                            get_questions.return_value = questions
                            preview_context = get_sms_preview_context(manager, post)
                            self.assertEquals(preview_context['questionnaire_code'], 'q01')
                            self.assertEquals(preview_context['questions'], questions)
                            self.assertEquals(preview_context['project'], project)
                            self.assertEquals(preview_context['example_sms'], "form code answer1")


    def test_should_get_question_list(self):
        form_model = Mock()
        form_model.fields = [{}]
        form_model.entity_defaults_to_reporter.return_value = False

        with patch("project.preview_views.get_preview_for_field") as preview_of_field:
            preview_of_field.return_value = {"description": "description"}
            questions = get_questions(form_model)
            self.assertEquals(questions[0]["description"], "description")

    def test_should_get_question_list_when_entity_is_reporter(self):
        form_model = Mock()
        form_model.fields = [{}]
        form_model.entity_defaults_to_reporter.return_value = True

        with patch("project.preview_views.get_preview_for_field") as preview_of_field:
            preview_of_field.return_value = {"description": "description"}
            with patch("project.preview_views.hide_entity_question") as hide_entity_question:
                hide_entity_question.return_value = {"description": "description"}
                questions = get_questions(form_model)
                self.assertEquals(len(questions), 1)

    def test_should_get_correct_context_for_web_preview(self):
        manager = {}
        form_model = {}
        form = Mock()
        form.cleaned_data = {
            "name": "project_name", "entity_type": "clinic", "language": "en", "goals": "goals", "activity_report": "yes",
        }
        post = {'profile_form': '{"activity_report": "yes" }',
                'project_state': 'Test'}
        web_questionnaire_form_creater = Mock()
        QuestionnaireForm = type('QuestionnaireForm', (Form, ), {"short_code_question_code": "eid"})
        with patch("project.preview_views.get_questionnaire_form_model_and_form") as questionnaire_form_model_and_form:
            questionnaire_form_model_and_form.return_value = form_model, form
            with patch.object(form, 'isValid') as is_valid:
                is_valid.return_value = True
                with patch("project.preview_views.WebQuestionnaireFormCreater") as web_questionnaire_form_creater:
                    web_questionnaire_form_creater.return_value = web_questionnaire_form_creater
                    with patch.object(web_questionnaire_form_creater, "create") as create_form:
                        create_form.return_value = QuestionnaireForm
                        with patch("project.preview_views.add_link_context") as add_link:
                            add_link.return_value = {'text': 'Add a datasender'}
                            web_preview_context = get_web_preview_context(manager, post)
                            project = web_preview_context['project']
                            self.assertEquals(project['activity_report'], "yes")
                            questionnaire_form = web_preview_context['questionnaire_form']
                            self.assertEquals(questionnaire_form.short_code_question_code, "eid")
                            self.assertEquals(web_preview_context['add_link']['text'], 'Add a datasender')

    def test_should_get_correct_add_link_for_project(self):
        project = Mock(spec=Project)
        project.entity_type = "reporter"
        project.id = "pid"
        add_link_dict = add_link_context(project)
        self.assertEquals(add_link_dict['text'], 'Add a datasender')
        self.assertEquals(add_link_dict['url'], "#")