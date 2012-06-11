import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.entity_type import get_all_entity_types
from mangrove.form_model.form_model import REPORTER
from accountmanagement.views import is_not_expired
from main.utils import get_database_manager
from project.forms import CreateProject
from project.helper import remove_reporter, get_preview_for_field, hide_entity_question
from project.models import Project
from project.views import get_example_sms, get_organization_telephone_number
from project.web_questionnaire_form_creator import WebQuestionnaireFormCreater, SubjectQuestionFieldCreator
from project.wizard_view import create_questionnaire


def get_questions(form_model):
    fields = form_model.fields
    if form_model.entity_defaults_to_reporter():
        fields = hide_entity_question(form_model.fields)
    questions = []
    for field in fields:
        question = get_preview_for_field(field)
        questions.append(question)

    return questions


def get_questionnaire_form_model_and_form(manager, project_info, post):
    entity_list = get_all_entity_types(manager)
    entity_list = remove_reporter(entity_list)
    form = CreateProject(entity_list, data=project_info)
    if form.is_valid():
        return create_questionnaire(post, manager, entity_type=form.cleaned_data['entity_type'],
            name=form.cleaned_data['name'], language=form.cleaned_data['language']), form
    return None, form

def get_sms_preview_context(manager, post, project_info):
    form_model, form = get_questionnaire_form_model_and_form(manager, project_info, post)
    if form.is_valid():
        example_sms = "%s" % (form_model.form_code)
        example_sms += get_example_sms(form_model.fields)

        return {"questionnaire_code": post["questionnaire-code"],
                   "questions": get_questions(form_model),
                   "project": project_info,
                   "example_sms": example_sms}
    return {}

@login_required(login_url='/login')
@is_not_expired
def sms_preview(request):
    manager = get_database_manager(request.user)
    context = {'org_number': get_organization_telephone_number(request)}
    project_info = json.loads(request.POST['profile_form'])
    context.update(get_sms_preview_context(manager, request.POST, project_info))

    return render_to_response("project/sms_instruction_preview.html", context, context_instance=RequestContext(request))


def add_link_context(project):
    if project.entity_type == REPORTER:
        text = _("Add a datasender")
        return {'url': '#', 'text': text}
    else:
        text = _("Register a %(subject)s") % {'subject': project.entity_type}
        return {'url': '#', 'text': text}

def get_web_preview_context(manager, post):
    project_info = json.loads(post['profile_form'])
    form_model, form = get_questionnaire_form_model_and_form(manager, project_info, post)
    if form.is_valid():
        project = Project(name=form.cleaned_data['name'], goals=form.cleaned_data['goals'],
            project_type='survey', entity_type=form.cleaned_data['entity_type'],
            activity_report=form.cleaned_data['activity_report'],
            state = post['project_state'], devices=[u'sms', u'web', u'smartPhone'],language=form.cleaned_data['language'])

        QuestionnaireForm = WebQuestionnaireFormCreater(SubjectQuestionFieldCreator(manager, project),
            form_model = form_model).create()
        questionnaire_form = QuestionnaireForm()
        context = {'project': project_info,
                   'questionnaire_form': questionnaire_form,
                    'add_link': add_link_context(project),}
        return context
    return {}

@login_required(login_url='/login')
@is_not_expired
def web_preview(request):
    return render_to_response("project/web_instruction_preview.html",
                              get_web_preview_context(get_database_manager(request.user),request.POST),
                              context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_not_expired
def smart_phone_preview(request):
    language_code = request.LANGUAGE_CODE
    instruction_template = "alldata/smart_phone_instruction_" + language_code + ".html"

    return render_to_response("project/smart_phone_instruction_preview.html",
                              {"instruction_template": instruction_template},
                              context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_not_expired
def questionnaire_sms_preview(request):
    manager = get_database_manager(request.user)
    context = {'org_number': get_organization_telephone_number(request)}
    project_info = Project.load(manager.database, request.POST['project_id'])
    context.update(get_sms_preview_context(manager, request.POST, project_info))

    return render_to_response("project/sms_instruction_preview.html", context, context_instance=RequestContext(request))

@login_required(login_url='/login')
@is_not_expired
def questionnaire_web_preview(request):
    return HttpResponse()
