import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_digest.decorators import httpdigest
import jsonpickle

from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.main.database import get_database_manager
from datawinners.submission.location import LocationBridge
from mangrove.datastore.entity import contact_by_short_code
from mangrove.errors import MangroveException
from mangrove.form_model.form_model import get_form_model_by_code, EntityFormModel
from mangrove.transport import TransportInfo
from mangrove.transport.player.parser import SMSParserFactory
from mangrove.transport.services.identification_number_service import IdentificationNumberService
from mangrove.transport.services.survey_response_service import SurveyResponseService


def _validate_request_format(request_message):
    return "reporter_id" in request_message and "message" in request_message


@csrf_exempt
@httpdigest
def post_submission(request):
    try:
        input_request = jsonpickle.decode(request.raw_post_data)
    except ValueError:
        return HttpResponse(status=400)
    manager = get_database_manager(request.user)
    player = ApiPlayer(manager)
    submission_reply = []

    if not isinstance(input_request, list):
        return HttpResponse(status=400)

    for request_message in input_request:
        if not _validate_request_format(request_message):
            return HttpResponse(status=400)
        reporter_id = request_message['reporter_id']
        submission_message = request_message['message']
        location_tree = LocationBridge(get_location_tree(), get_location_hierarchy)
        success, message = player.submit(submission_message, reporter_id, location_tree)
        submission_reply.append({"success": success, 'message': message})
    return HttpResponse(content_type='application/json', content=json.dumps(submission_reply))


class ApiPlayer(object):

    def __init__(self, dbm):
        self.dbm = dbm

    def _create_survey_response(self, form_code, reporter_id, values):
        service = SurveyResponseService(self.dbm)
        transport_info = TransportInfo(transport='api', source=reporter_id, destination='')
        # ds-registered
        # ds-linked
        # no of answers
        response = service.save_survey(form_code, values, [], transport_info, reporter_id)
        return response

    def submit(self, submission, reporter_id, location_tree):
        try:
            form_code, values, extra_data = SMSParserFactory().getSMSParser(submission, self.dbm).parse(submission)
            form_model = get_form_model_by_code(self.dbm, form_code)

            if isinstance(form_model, EntityFormModel):
                response = self._create_identification_number(form_code, values, location_tree)
            else:
                response = self._create_survey_response(form_code, reporter_id, values)
        except MangroveException as e:
            return False, e.message
        return response.success, 'submitted successfully'

    def _create_identification_number(self,form_code, values, location_tree):
        service = IdentificationNumberService(self.dbm)
        response = service.save_identification_number(form_code, values, location_tree)
        return response
