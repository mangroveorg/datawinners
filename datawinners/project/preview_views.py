import json

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.common.authorization import is_data_sender
from datawinners.project.models import Project
from mangrove.form_model.form_model import FormModel

from datawinners import settings
from datawinners.accountmanagement.decorators import valid_web_user
from datawinners.entity.helper import get_organization_telephone_number
from datawinners.entity.views import get_example_sms
from datawinners.main.database import get_database_manager
from datawinners.project.helper import  get_preview_for_field
from datawinners.project.subject_question_creator import SubjectQuestionFieldCreator
from datawinners.project.submission_form import SurveyResponseForm
from datawinners.project.wizard_view import create_questionnaire


def get_questions(form_model):
    fields = form_model.fields
    return [get_preview_for_field(field) for field in fields]


def get_questionnaire_form_model(manager, project_info, post):
    return create_questionnaire(post, manager, name=unicode(project_info.get('name')),
                                language=unicode(project_info.get('language')), reporter_id=None)

def get_sms_preview_context(manager, post, project_info):
    form_model = project_info if isinstance(project_info, FormModel) else get_questionnaire_form_model(manager, project_info, post)
    example_sms = "%s" % form_model.form_code
    example_sms += get_example_sms(form_model.fields)
    return {"questionnaire_code": post["questionnaire-code"],
            "questions": get_questions(form_model),
            "project_name": form_model.name,
            "example_sms": example_sms}


@valid_web_user
def sms_preview(request):
    manager = get_database_manager(request.user)
    context = {'org_number': get_organization_telephone_number(request)}
    project_info = json.loads(request.POST['profile_form'])
    context.update(get_sms_preview_context(manager, request.POST, project_info))

    return render_to_response("project/sms_instruction_preview.html", context, context_instance=RequestContext(request))



def get_web_preview_context_from_project_data(manager, request, project_info):
    is_datasender = is_data_sender(request)
    form_model = get_questionnaire_form_model(manager, project_info, request.POST)
    questionnaire_form = SurveyResponseForm(form_model)
    return {'project': project_info,
            'is_datasender': is_datasender,
            'questionnaire_form': questionnaire_form}

def get_web_preview_context_from_existing_project(project_info):
    return {'project': project_info,
            'questionnaire_form': SurveyResponseForm(project_info)}


@valid_web_user
def web_preview(request):
    project_info = json.loads(request.POST['profile_form'])
    manager = get_database_manager(request.user)

    return render_to_response("project/web_instruction_preview.html",
                              get_web_preview_context_from_project_data(manager, request, project_info),
                              context_instance=RequestContext(request))


@valid_web_user
def smart_phone_preview(request):
    language_code = request.LANGUAGE_CODE
    instruction_template = "alldata/smart_phone_instruction_" + language_code + ".html"

    return render_to_response("project/smart_phone_instruction_preview.html",
            {"instruction_template": instruction_template},
                              context_instance=RequestContext(request))




