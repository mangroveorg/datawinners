import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from mangrove.datastore.entity_type import get_all_entity_types
from accountmanagement.views import is_not_expired
from project import helper
from project.forms import CreateProject
from project.helper import remove_reporter
from project.wizard_view import create_questionnaire


def get_questions(form_model):
    return {}

def get_sms_preview_context(manager, post):
    entity_list = get_all_entity_types(manager)
    entity_list = remove_reporter(entity_list)

    project_info = json.loads(post['profile_form'])
    form = CreateProject(entity_list, data=project_info)

    form_model = create_questionnaire(post, manager, entity_type=form.cleaned_data['entity_type'],
                                      name=form.cleaned_data['name'], language=form.cleaned_data['language'])

    context = {"questionnaire_code": post["questionnaire-code"],
               "questions": get_questions(form_model),
               "project": project_info}

    return context

@login_required(login_url='/login')
@is_not_expired
def sms_preview(request):

    return render_to_response("project/sms_instruction_preview.html")


