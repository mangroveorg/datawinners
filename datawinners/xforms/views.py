from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mangrove.form_model.form_model import  FormModel
from mangrove.transport import Request
from mangrove.transport.facade import TransportInfo
from mangrove.transport.player.player import WebPlayer
from datawinners.accountmanagement.httpauth import logged_in_or_basicauth
from datawinners.alldata.helper import get_all_project_for_user
from datawinners.main.utils import get_database_manager
from datawinners.xforms.xml_to_dict_parser import xmltodict


@logged_in_or_basicauth()
def formList(request):
    rows = get_all_project_for_user(request.user)
    projects = [(row['value']['name'], row['value']['qid']) for row in rows]

    base_url = request.build_absolute_uri().replace(request.path, "")
    return render_to_response(
        "xforms/odk_list_forms.xml",
            {"projects": projects,
             "base_url": base_url},
        mimetype="text/xml",
        context_instance=RequestContext(request))


@csrf_exempt
@require_http_methods(['POST'])
def submission(request):
    submission_data = request.FILES.get("xml_submission_file").read()
    submission_data_dict = xmltodict(submission_data)
    for key in submission_data_dict.keys() :
        submission_data_dict[key] = ",".join(submission_data_dict[key])

    web_player = WebPlayer(get_database_manager(request.user))
    mangrove_request = Request(message=submission_data_dict,
        transportInfo=
        TransportInfo(transport="web",
            source=request.user,
            destination=""
        ))

    web_player.accept(mangrove_request)
    response = render_to_response("xforms/submission.html")
    response.status_code = 201
    response['Location'] = request.build_absolute_uri(request.path)
    return response


@logged_in_or_basicauth()
def xform(request, questionnaire_code=None):
    questionnaire = FormModel.get(get_database_manager(request.user), questionnaire_code)

    return render_to_response(
        "xforms/xform.xml",
            {"questionnaire": questionnaire},
        mimetype="text/xml",
        context_instance=RequestContext(request))
