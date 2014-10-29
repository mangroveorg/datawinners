# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import unittest

from django.core.urlresolvers import reverse
from mock import Mock, patch, MagicMock

from datawinners.project.views.submission_views import get_filterable_fields
from mangrove.transport import Response
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import TextField, DateField, UniqueIdField
from datawinners.entity.forms import ReporterRegistrationForm
from datawinners.project.models import Reminder, RemindTo, ReminderMode
from datawinners.project.views.views import _format_reminders, SubjectWebQuestionnaireRequest
from datawinners.project.preview_views import get_sms_preview_context, get_questions, get_web_preview_context_from_project_data
from datawinners.project.utils import make_subject_links
from datawinners.project.views.views import append_success_to_context, formatted_data
from datawinners.project.wizard_view import get_preview_and_instruction_links, _get_changed_data
from datawinners.questionnaire.questionnaire_builder import get_max_code
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.project import Project


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
        # self.assertEqnual('/project/delete_reminder/test_project/1/', formated_reminders[0]['delete_link'])

        self.assertEqual('On Deadline', formated_reminders[0]['when'])
        self.assertEqual('Datasenders Without Submissions', formated_reminders[0]['to'])

        self.assertEqual('2 days Before Deadline', formated_reminders[1]['when'])
        self.assertEqual('All Datasenders', formated_reminders[1]['to'])

    def test_should_return_subject_project_links(self):
        project_id = "1"
        entity_type = "entity_type"
        subject_links = make_subject_links(project_id, entity_type)
        self.assertEqual(reverse('registered_subjects', args=[project_id, entity_type]), subject_links['subjects_link'])
        self.assertEqual(reverse('edit_my_subject_questionnaire', args=[project_id, entity_type]), subject_links['subjects_edit_link'])
        self.assertEqual(reverse('subject_registration_form_preview', args=[project_id, entity_type]),
                         subject_links['subject_registration_preview_link'])
        self.assertEqual(reverse('registered_subjects', args=[project_id, entity_type]),
                         subject_links['registered_subjects_link'])
        self.assertEqual(reverse('subject_questionnaire', args=[project_id, entity_type]),
                         subject_links['register_subjects_link'])
        self.assertEqual(reverse('subject_questionnaire', args=[project_id, entity_type]) + "?web_view=True",
                         subject_links['register_subjects_link_web_view'])

    def test_should_get_preview_and_instruction_links(self):
        with patch("datawinners.project.wizard_view.reverse") as reverse:
            reverse.side_effect = lambda *args, **kw: "/project/%s" % args[0]
            links = get_preview_and_instruction_links()
            self.assertEqual(links["sms_preview"], "/project/sms_preview")
            self.assertEqual(links["web_preview"], "/project/web_preview")
            self.assertEqual(links["smart_phone_preview"], "/project/smart_phone_preview")

    def test_should_get_correct_context_for_sms_preview(self):
        questions = {}
        manager = {}
        form_model = Mock()
        form_model.fields = [{}]
        form_model.form_code = "form code"
        form_model.name="project_name"
        project_form = Mock()
        project_form.cleaned_data = {
            "name": "project_name", "entity_type": "clinic", "language": "en"
        }

        post = {"questionnaire-code": "q01",
                "question-set": "",
                "profile_form": '{"name":"project_name", "entity_type":"clinic", "language":"en"}'}

        project_info = json.loads(post['profile_form'])
        with patch("datawinners.project.preview_views.create_questionnaire") as questionnaire:
            questionnaire.return_value = form_model
            with patch("datawinners.project.preview_views.get_questions") as get_questions:
                get_questions.return_value = questions
                preview_context = get_sms_preview_context(manager, post, project_info)

                self.assertEquals(preview_context['questionnaire_code'], 'q01')
                self.assertEquals(preview_context['questions'], questions)
                self.assertEquals(preview_context['project_name'], "project_name")
                self.assertEquals(preview_context['example_sms'], "form code answer1")


    def test_should_get_question_list(self):
        form_model = Mock()
        form_model.fields = [{}]

        with patch("datawinners.project.preview_views.get_preview_for_field") as preview_of_field:
            preview_of_field.return_value = {"description": "description"}
            questions = get_questions(form_model)
            self.assertEquals(questions[0]["description"], "description")

    def test_should_get_correct_context_for_web_preview(self):
        manager = {}
        form_model = {}

        project_info = {"name": "project_name", "goals": "des", "entity_type": "clinic",
                        "language": "en"}
        with patch("datawinners.project.preview_views.get_questionnaire_form_model") as questionnaire_form_model:
            questionnaire_form_model.return_value = form_model
            with patch("datawinners.project.preview_views.SurveyResponseForm") as SurveyResponseForm:
                mock_form = Mock(spec=SurveyResponseForm)
                SurveyResponseForm.return_value = mock_form
                request = MagicMock()
                request.POST = {}
                web_preview_context = get_web_preview_context_from_project_data(manager, request, project_info)
                questionnaire_form = web_preview_context['questionnaire_form']
                self.assertEquals(questionnaire_form, mock_form)


    def test_should_get_correct_instruction_and_preview_links_for_questionnaire(self):
        with patch("datawinners.project.views.views.reverse") as reverse:
            reverse.side_effect = lambda *args, **kw: "/project/%s" % args[0]
            links = get_preview_and_instruction_links()
            self.assertEqual(links["sms_preview"], "/project/sms_preview")
            self.assertEqual(links["web_preview"], "/project/web_preview")
            self.assertEqual(links["smart_phone_preview"], "/project/smart_phone_preview")


    def test_should_append_success_status_to_context_when_no_error(self):
        context = {}
        form = Mock(spec=ReporterRegistrationForm)
        form.errors = []
        new_context = append_success_to_context(context, form)
        self.assertTrue(new_context['success'])


    def test_should_append_failed_status_to_context_when_has_error(self):
        context = {}
        form = Mock(spec=ReporterRegistrationForm)
        form.errors = ['']
        new_context = append_success_to_context(context, form)
        self.assertFalse(new_context['success'])


    def test_should_return_max_code_in_questionnaire(self):
        fields = [TextField(name="f1", code="q1", label="f1"),
                  TextField(name="f2", code="q2", label="f2"),
                  TextField(name="f3", code="q3", label="f3"),
                  TextField(name="f3", code="q4", label="f4"),
                  TextField(name="f5", code="q5", label="f5")]
        self.assertEqual(5, get_max_code(fields))


    def test_should_return_one_in_questionnaire_without_start_with_q(self):
        fields = [TextField(name="f1", code="c1", label="f1"),
                  TextField(name="f2", code="c2", label="f2"),
                  TextField(name="f3", code="c3", label="f3"),
                  TextField(name="f3", code="c4", label="f4"),
                  TextField(name="f5", code="c5", label="f5")]
        self.assertEqual(1, get_max_code(fields))


    def test_should_return_origin_value_for_item_is_non_tuple_data(self):
        field_values = [['string']]
        data = formatted_data(field_values)
        self.assertEqual(data, [['string']])
        self.assertEqual(field_values, [['string']])


    def test_should_return_formatted_value_for_item_is_tuple_data_and_origin_not_changed(self):
        field_values = [[('key', 'value'), 'string']]
        data = formatted_data(field_values)
        self.assertEqual(data, [['key</br>(value)', 'string']])
        self.assertEqual(field_values, [[('key', 'value'), 'string']])

    def test_should_get_changed_data_when_project_is_edited(self):
        project_info = {'name':'changed name','language':'en'}
        project = Project(dbm=Mock(spec= DatabaseManager), name='old name', language='en',
                            form_code="change_form", fields=[])
        changed_dict = _get_changed_data(project,project_info)
        self.assertDictEqual({'Name':'changed name'},changed_dict)

class TestSubjectWebQuestionnaireRequest(unittest.TestCase):

    def test_should_return_date_and_unique_id_fields_from_questionnaire(self):
        fields = [
                                TextField("Some word question", "q1", "Some word question"),
                                UniqueIdField("goats", "What goat are you reporting on?", "q2", "What goat are you reporting on?"),
                                DateField("When did you buy the goat?", "q3", "When did you buy the goat?", "dd.mm.yyyy"),
                                DateField("When did you sell the goat?", "q4", "When did you sell the goat?", "mm.yyyy")
                               ]

        fields_array = get_filterable_fields(fields)

        self.assertEqual(len(fields_array), 3)
        self.assertDictEqual(fields_array[0], {'type': 'unique_id', 'code': 'q2', 'entity_type': 'goats'})
        self.assertDictEqual(fields_array[1], {'type': 'date', 'code': 'q3', 'label': 'When did you buy the goat?',
                'is_month_format': False, 'format': 'dd.mm.yyyy'})
        self.assertDictEqual(fields_array[2], {'type': 'date', 'code': 'q4', 'label': 'When did you sell the goat?',
                'is_month_format': True, 'format': 'mm.yyyy'})

    def test_should_return_unique_entries_when_multiple_unique_id_fields_of_same_type_are_present_from_questionnaire(self):
        fields = [
                                TextField("Some word question", "q1", "Some word question"),
                                UniqueIdField("goats", "What goat are you reporting on?", "q2", "What goat are you reporting on?"),
                                UniqueIdField("chicken", "What chicken are you reporting on?", "q3", "What chicken are you reporting on?"),
                                UniqueIdField("goats", "What goat are you reporting on?", "q4", "What goat are you reporting on?"),
                               ]

        fields_array = get_filterable_fields(fields)

        self.assertEqual(len(fields_array), 2)
        self.assertDictEqual(fields_array[0], {'type': 'unique_id', 'code': 'q2', 'entity_type': 'goats'})
        self.assertDictEqual(fields_array[1], {'type': 'unique_id', 'code': 'q3', 'entity_type': 'chicken'})

    class StubSubjectWebQuestionnaireRequest(SubjectWebQuestionnaireRequest):
        def __init__(self, request, project_id, entity_type,form_list):
            self.form_list = form_list
            SubjectWebQuestionnaireRequest.__init__(self, request, project_id, entity_type)
            self.form_model = MagicMock()


        def _initialize(self, project_id, entity_type):
            self.manager = None
            self.questionnaire = Mock(spec=FormModel)
            self.is_data_sender = True
            self.disable_link_class, self.hide_link_class = None, None
            self.form_code = None
            self.form_model = None
            self.entity_type = entity_type


        def player_response(self, created_request):
            return Response(success=True)

        def success_message(self, response_short_code):
            return ""

        def _update_form_context(self, form_context, questionnaire_form, web_view_enabled=True):
            return form_context