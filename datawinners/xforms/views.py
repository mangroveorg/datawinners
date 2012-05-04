from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.transport import Request
from mangrove.transport.facade import TransportInfo
from mangrove.transport.player.player import XFormPlayer
from mangrove.transport.xforms.xform import list_all_forms, xform_for
from datawinners.accountmanagement.httpauth import logged_in_or_basicauth
from datawinners.alldata.helper import get_all_project_for_user
from datawinners.main.utils import get_database_manager
from datawinners.messageprovider.messages import exception_messages, WEB


@logged_in_or_basicauth()
def formList(request):
    rows = get_all_project_for_user(request.user)
    form_tuples = [(row['value']['name'], row['value']['qid']) for row in rows]
    xform_base_url = request.build_absolute_uri('/xforms')
    return HttpResponse(content=list_all_forms(form_tuples, xform_base_url), mimetype="text/xml")


def return_error_response(errors):
    response = render_to_response("xforms/errors.html",
            {'errors': errors})
    response.status_code = 400
    HttpResponse()

    return response


@csrf_exempt
@require_http_methods(['POST'])
def submission(request):
    request_user = request.user
    manager = get_database_manager(request_user)
    player = XFormPlayer(manager)
    reporter_id = request_user.get_profile().reporter_id
    reporter_name = get_by_short_code(manager, reporter_id, ["reporter"]).data['name']['value']
    mangrove_request = Request(message=(request.FILES.get("xml_submission_file").read()),
        transportInfo=
        TransportInfo(transport="xform",
            source=(reporter_id, reporter_name),
            destination=""
        ))
    try:
        response = player.accept(mangrove_request)
        if response.errors:
            return return_error_response(response.errors)
    except DataObjectNotFound:
        message = exception_messages.get(DataObjectNotFound).get(WEB)
        error_message = message
        return return_error_response(error_message)

    response = HttpResponse(status=201)
    response['Location'] = request.build_absolute_uri(request.path)
    return response


@logged_in_or_basicauth()
def xform(request, questionnaire_code=None):
    return HttpResponse(content=xform_for(get_database_manager(request.user), questionnaire_code),
        mimetype="text/xml")
