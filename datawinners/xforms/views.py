from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mangrove.transport import Request
from mangrove.transport.facade import TransportInfo
from mangrove.transport.player.player import XFormPlayer
from mangrove.transport.xforms.xform import list_all_forms, xform_for
from datawinners.accountmanagement.httpauth import logged_in_or_basicauth
from datawinners.alldata.helper import get_all_project_for_user
from datawinners.main.utils import get_database_manager


@logged_in_or_basicauth()
def formList(request):
    rows = get_all_project_for_user(request.user)
    form_tuples = [(row['value']['name'], row['value']['qid']) for row in rows]
    xform_base_url = request.build_absolute_uri('/xforms')
    return HttpResponse(content=list_all_forms(form_tuples, xform_base_url), mimetype="text/xml")


@csrf_exempt
@require_http_methods(['POST'])
def submission(request):
    player = XFormPlayer(get_database_manager(request.user))
    mangrove_request = Request(message=(request.FILES.get("xml_submission_file").read()),
        transportInfo=
        TransportInfo(transport="xform",
            source=request.user,
            destination=""
        ))

    player.accept(mangrove_request)
    response = HttpResponse(status=201)
    response['Location'] = request.build_absolute_uri(request.path)
    return response


@logged_in_or_basicauth()
def xform(request, questionnaire_code=None):
    return HttpResponse(content=xform_for(get_database_manager(request.user), questionnaire_code), mimetype="text/xml")
