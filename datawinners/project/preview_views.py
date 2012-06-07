import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from mangrove.datastore.entity_type import get_all_entity_types
from accountmanagement.views import is_not_expired
from main.utils import get_database_manager
from project import helper
from project.forms import CreateProject
from project.helper import remove_reporter, get_preview_for_field, hide_entity_question
from project.views import get_example_sms, get_organization_telephone_number
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

def get_sms_preview_context(manager, post):
    entity_list = get_all_entity_types(manager)
    entity_list = remove_reporter(entity_list)

    project_info = json.loads(post['profile_form'])
    form = CreateProject(entity_list, data=project_info)
    if form.is_valid():
        form_model = create_questionnaire(post, manager, entity_type = form.cleaned_data['entity_type'],
                                      name=form.cleaned_data['name'], language=form.cleaned_data['language'])

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
    context.update(get_sms_preview_context(manager, request.POST))

    return render_to_response("project/sms_instruction_preview.html", context, context_instance=RequestContext(request))
