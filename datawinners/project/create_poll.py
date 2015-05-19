import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.main.database import get_database_manager
from datawinners.project import helper
from datawinners.project.views.create_questionnaire import validate_questionnaire_name_and_code
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
from mangrove.form_model.project import Project
from django.utils.translation import ugettext as _


def _is_project_name_unique(error_message, name_has_errors, questionnaire):
    if not questionnaire.is_project_name_unique():
        name_has_errors = True
        error_message["name"] = _("Questionnaire with same name already exists.")
    return name_has_errors


def _create_poll(manager, questionnaire, request):
    question_set = [{'title': request.POST.get('question'), 'type': 'text', "is_entity_question": False,
                     "code": 'q1', "name": request.POST.get('question'), 'required': True,
                     "parent_field_code": '',
                     "instruction": "Answer must be a text", 'label': request.POST.get('question', 'label')}]
    QuestionnaireBuilder(questionnaire, manager).update_questionnaire_with_questions(question_set)
    questionnaire.update_doc_and_save()


def _construct_questionnaire(request):
    manager = get_database_manager(request.user)
    questionnaire_code = helper.generate_questionnaire_code(manager)
    questionnaire = Project(manager, name=request.POST.get('poll_name'),
                            fields=[], form_code=questionnaire_code, language=request.LANGUAGE_CODE,
                            devices=[u'sms', u'web', u'smartPhone'], is_poll=True)
    return manager, questionnaire


def create_poll_questionnaire(request):
    manager, questionnaire = _construct_questionnaire(request)
    project_name_unique = False
    error_message = {}
    project_name_unique = _is_project_name_unique(error_message, project_name_unique, questionnaire)
    if not project_name_unique:
        _create_poll(manager, questionnaire, request)
        return HttpResponse(json.dumps({'success': True, 'project_id': questionnaire.id, 'project_code': questionnaire.form_code}))
    return HttpResponse(json.dumps({'success': False,
                                    'error_message': error_message,
                                    'project_name_unique': project_name_unique}))


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def create_poll(request):
    if request.method == 'POST':
        return create_poll_questionnaire(request)