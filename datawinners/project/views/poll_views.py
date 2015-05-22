from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from datawinners.accountmanagement.decorators import is_not_expired, is_datasender
from datawinners.main.database import get_database_manager
from datawinners.project.helper import is_project_exist
from datawinners.project.utils import make_project_links
from datawinners.project.views.views import get_project_link
from mangrove.form_model.project import Project
from django.template.context import RequestContext
from django.core.urlresolvers import reverse


@login_required
@csrf_exempt
@is_not_expired
@is_project_exist
@is_datasender
def poll(request, project_id):
    manager = get_database_manager(request.user)
    questionnaire = Project.get(manager, project_id)
    project_links = get_project_link(questionnaire)

    return render_to_response('project/poll.html', RequestContext(request, {
        'project': questionnaire,
        'project_links': project_links,


    }))
