import json
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners import settings
from datawinners.accountmanagement.decorators import valid_web_user
from datawinners.entity.helper import get_organization_telephone_number
from datawinners.entity.views import get_example_sms
from datawinners.main.database import get_database_manager
from datawinners.project.web_questionnaire_form import SurveyResponseForm
from mangrove.form_model.form_model import REPORTER
from datawinners.project.helper import  get_preview_for_field, hide_entity_question
from datawinners.project.models import Project
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from datawinners.project.wizard_view import create_questionnaire
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


def get_questions(form_model):
    fields = form_model.fields
    if form_model.is_entity_type_reporter():
        fields = hide_entity_question(form_model.fields)

    return [get_preview_for_field(field) for field in fields]


def get_questionnaire_form_model(manager, project_info, post):
    return create_questionnaire(post, manager, entity_type=REPORTER_ENTITY_TYPE,
                                name=unicode(project_info['name']), language=unicode(project_info['language']))

def get_sms_preview_context(manager, post, project_info):
    form_model = get_questionnaire_form_model(manager, project_info, post)
    example_sms = "%s" % form_model.form_code
    example_sms += get_example_sms(form_model.fields)
    return {"questionnaire_code": post["questionnaire-code"],
            "questions": get_questions(form_model),
            "project": project_info,
            "example_sms": example_sms}


@valid_web_user
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


def get_web_preview_context(manager, post, project_info):
    form_model = get_questionnaire_form_model(manager, project_info, post)
    project = Project(name=unicode(project_info['name']),
                      #goals=unicode(project_info['goals']),
                      project_type='survey',
                      entity_type=unicode(REPORTER),
                      activity_report=unicode(project_info['activity_report']),
                       devices=[u'sms', u'web', u'smartPhone'],
                      language=unicode(project_info['language']))

    questionnaire_form = SurveyResponseForm(form_model,SubjectQuestionFieldCreator(manager, project))
    return {'project': project_info,
            'questionnaire_form': questionnaire_form,
            'add_link': add_link_context(project), }


@valid_web_user
def web_preview(request):
    project_info = json.loads(request.POST['profile_form'])
    manager = get_database_manager(request.user)

    return render_to_response("project/web_instruction_preview.html",
                              get_web_preview_context(manager, request.POST, project_info),
                              context_instance=RequestContext(request))


@valid_web_user
def smart_phone_preview(request):
    language_code = request.LANGUAGE_CODE
    instruction_template = "alldata/smart_phone_instruction_" + language_code + ".html"

    return render_to_response("project/smart_phone_instruction_preview.html",
            {"instruction_template": instruction_template},
                              context_instance=RequestContext(request))


@valid_web_user
def questionnaire_sms_preview(request):
    manager = get_database_manager(request.user)
    context = {'org_number': get_organization_telephone_number(request)}
    project_info = Project.load(manager.database, request.POST['project_id'])
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if project_info.is_deleted():
        return HttpResponseRedirect(dashboard_page)
    if project_info:
        context.update(get_sms_preview_context(manager, request.POST, project_info))

    return render_to_response("project/sms_instruction_preview.html", context, context_instance=RequestContext(request))


@valid_web_user
def questionnaire_web_preview(request):
    manager = get_database_manager(request.user)
    project_info = Project.load(manager.database, request.POST["project_id"])
    dashboard_page = settings.HOME_PAGE + "?deleted=true"
    if project_info.is_deleted():
        return HttpResponseRedirect(dashboard_page)
    context = get_web_preview_context(manager, request.POST, project_info) if project_info else {}
    return render_to_response("project/web_instruction_preview.html",
                              context,
                              context_instance=RequestContext(request))
