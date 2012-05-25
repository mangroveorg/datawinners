import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_digest.decorators import httpdigest
from mangrove.transport import Request
from mangrove.transport.facade import TransportInfo
from mangrove.transport.player.player import XFormPlayer
from mangrove.transport.xforms.xform import list_all_forms, xform_for
from datawinners.accountmanagement.models import Organization
from datawinners.alldata.helper import get_all_project_for_user
from datawinners.main.utils import get_database_manager
from django.contrib.gis.utils import GeoIP

logger = logging.getLogger("datawinners.xform")

def restrict_request_country(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        org = Organization.objects.get(org_id=user.get_profile().org_id)
        try :
            country_code = GeoIP().country_code(request.META.get('REMOTE_ADDR'))
        except Exception as e:
            logger.exception("Error resolving country from IP : %s"%e)
            raise
        if country_code is None or org.country.code == country_code:
            return f(*args, **kw)
        return HttpResponse(status=401)

    return wrapper


@csrf_exempt
@httpdigest
@restrict_request_country
def formList(request):
    rows = get_all_project_for_user(request.user)
    form_tuples = [(row['value']['name'], row['value']['qid']) for row in rows]
    xform_base_url = request.build_absolute_uri('/xforms')
    return HttpResponse(content=list_all_forms(form_tuples, xform_base_url), mimetype="text/xml")


@csrf_exempt
@require_http_methods(['POST'])
@httpdigest
@restrict_request_country
def submission(request):
    request_user = request.user
    manager = get_database_manager(request_user)
    player = XFormPlayer(manager)
    try:
        mangrove_request = Request(message=(request.FILES.get("xml_submission_file").read()),
            transportInfo=
            TransportInfo(transport="smartPhone",
                source=request_user.email,
                destination=''
            ))
        response = player.accept(mangrove_request)
        if response.errors:
            logger.error("Error in submission : %s" % '\n'.join(response.errors))
            return HttpResponseBadRequest()
    except Exception as e:
        logger.exception("Exception in submission : %s" % e)
        return HttpResponseBadRequest()

    response = HttpResponse(status=201)
    response['Location'] = request.build_absolute_uri(request.path)
    return response


@csrf_exempt
@httpdigest
def xform(request, questionnaire_code=None):
    request_user = request.user
    form = xform_for(get_database_manager(request_user), questionnaire_code, request_user.get_profile().reporter_id)
    return HttpResponse(content= form,
        mimetype="text/xml")
