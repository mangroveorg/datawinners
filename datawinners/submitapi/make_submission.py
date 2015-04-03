from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_digest.decorators import httpdigest
import json
import jsonpickle
from datawinners.dataextraction.helper import convert_to_json_file_download_response

from datawinners.main.database import get_database_manager
from datawinners.utils import get_organization
from mangrove.transport.player.new_players import SubmitApiPlayer

@csrf_exempt
@httpdigest
def post_submission(request):
    input_request = jsonpickle.decode(request.raw_post_data)
    organization = get_organization(request)
    manager = get_database_manager(request.user)
    # client = SubmitClient()
    player = SubmitApiPlayer(manager)
    result = {}
    submission_reply = []
    submissions = input_request.get('message',[])
    reporter_id = input_request.get('reporter_id')
    for submission in submissions:
        # success, message = client.submit_questionnaire(manager, submission, reporter_id)
        #client.submit_questionnaire(manager, submission, reporter_id)
        success, message = player.submit(submission, reporter_id)
        submission_reply.append({ "success": success, 'message':message })
        # organization.increment_incoming_submission_count()
    result['submission_reply'] = submission_reply

    return HttpResponse(content_type='application/json', content=json.dumps(result))
