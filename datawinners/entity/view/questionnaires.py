import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.main.database import get_database_manager
from datawinners.project.models import get_simple_project_names, get_all_project_names


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
def get_existing_questionnaires(request):
    dbm = get_database_manager(request.user)
    existing_simple_questionnaires = get_simple_project_names(dbm)
    return HttpResponse(json.dumps({
                                    'questionnaires': existing_simple_questionnaires
                                   }), content_type='application/json')


def get_questionnaires_and_polls(request):
    dbm = get_database_manager(request.user)
    existing_questionnaires_and_polls = get_all_project_names(dbm)
    return HttpResponse(json.dumps({
                                    'questionnaires': existing_questionnaires_and_polls
                                   }), content_type='application/json')
