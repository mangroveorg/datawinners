from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_digest.decorators import httpdigest
import json
import jsonpickle
from datawinners.dataextraction.helper import convert_to_json_file_download_response
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy

from datawinners.main.database import get_database_manager
from datawinners.submission.location import LocationBridge
from datawinners.utils import get_organization
from mangrove.transport.player.new_players import SubmitApiPlayer

@csrf_exempt
@httpdigest
def post_submission(request):
    input_request = jsonpickle.decode(request.raw_post_data)
    manager = get_database_manager(request.user)
    player = SubmitApiPlayer(manager)
    result = {}
    submission_reply = []
    submissions = input_request.get('message',[])
    reporter_id = input_request.get('reporter_id')
    location_tree = LocationBridge(get_location_tree(), get_location_hierarchy)
    for submission in submissions:
        success, message = player.submit(submission, reporter_id, location_tree)
        submission_reply.append({ "success": success, 'message':message })
    result['submission_reply'] = submission_reply

    return HttpResponse(content_type='application/json', content=json.dumps(result))
