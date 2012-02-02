from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from datawinners.accountmanagement.views import is_new_user
from datawinners.alldata.helper import get_all_project_for_user, get_visibility_settings_for
from datawinners.main.utils import get_database_manager
from datawinners.project.models import ProjectState, Project
from datawinners.project.views import project_overview, project_data, project_results, web_questionnaire
from mangrove.form_model.form_model import FormModel
from datawinners.submission.models import DatawinnerLog
from datawinners.utils import get_organization
from datawinners.entity.views import create_subject

@login_required(login_url='/login')
@is_new_user
def index(request):
    reporter_id = request.user.get_profile().reporter_id
    manager = get_database_manager(request.user)
    project_list = []
    rows = get_all_project_for_user(request.user)
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    for row in rows:
        analysis = log = "#"
        disabled = "disable_link"
        project_id = row['value']['_id']
        project = Project.load(manager.database, project_id)
        questionnaire = manager.get(project['qid'], FormModel)
        questionnaire_code = questionnaire.form_code
        link = reverse(project_overview, args=[project_id])
        web_submission_link = reverse(web_questionnaire, args=[project_id])
        if project.state != ProjectState.INACTIVE:
            disabled = ""
            analysis = reverse(project_data, args=[project_id, questionnaire_code])
            log = reverse(project_results, args=[project_id, questionnaire_code])

        web_submission_link_disabled = 'disable_link'
        if 'web' in row['value']['devices']:
            web_submission_link_disabled = ""
        create_subjects_link = ''
        if 'no' in row['value']['activity_report']:
            create_subjects_link = reverse(create_subject,args=[project.entity_type])
        project_info = dict(name=row['value']['name'], created=row['value']['created'], type=row['value']['project_type'],
                       link=link, log=log, analysis=analysis, disabled=disabled, web_submission_link=web_submission_link,
                       web_submission_link_disabled=web_submission_link_disabled, create_subjects_link=create_subjects_link,
                       entity_type=project.entity_type)
        project_list.append(project_info)
    return render_to_response('alldata/index.html', {'projects': project_list, 'disable_link_class': disable_link_class, 'hide_link_class':hide_link_class},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
def failed_submissions(request):
    logs = DatawinnerLog.objects.all()
    organization = get_organization(request)
    org_logs = [log for log in logs if log.organization == organization]
    return render_to_response('alldata/failed_submissions.html', {'logs': org_logs},
                              context_instance=RequestContext(request))
