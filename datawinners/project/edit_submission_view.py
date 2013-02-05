from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from accountmanagement.views import is_not_expired, session_not_expired
from main.utils import get_database_manager
from mangrove.form_model.form_model import get_form_model_by_code, FormModel
from mangrove.transport.submissions import get_submission_by_id
from project.models import Project
from project.views import web_questionnaire
from project.web_questionnaire_form_creator import WebQuestionnaireFormCreator, SubjectQuestionFieldCreator

@login_required(login_url='/login')
@session_not_expired
@is_not_expired
def edit_submission(request, project_id=None, questionnaire_code=None, submission_id=None):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    form_model = FormModel.get(manager, project.qid)
    is_data_sender = request.user.get_profile().reporter
    template = "project/web_questionnaire.html"

    QuestionnaireForm = WebQuestionnaireFormCreator(SubjectQuestionFieldCreator(manager, project),
        form_model=form_model).create()
    submission = get_submission_by_id(manager,submission_id)

    if request.method == 'GET':
        questionnaire_form = QuestionnaireForm()
        _map_submission_and_questionnaire(submission[0],questionnaire_form)
        form_context = _make_form_context(questionnaire_form,project)
        print submission[0].data_record.data
        return render_to_response(template, form_context,
            context_instance=RequestContext(request))
    if request.method == 'POST':
        return web_questionnaire(request,project_id)

def _make_form_context(questionnaire_form, project):
    return {'questionnaire_form': questionnaire_form,
            'project': project,
    }

def _map_submission_and_questionnaire(submission,questionnaire_form):
    for field_name, field in questionnaire_form.fields.iteritems():
        if not field.widget.is_hidden:
            field.initial = submission.values.get(field_name.lower())

