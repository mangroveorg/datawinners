import base64
import json
from django.http import HttpResponseBadRequest, HttpResponse
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.main.database import get_database_manager
from datawinners.messageprovider.messages import SMART_PHONE
from datawinners.submission.views import check_quotas_and_update_users
from datawinners.xforms.views import sp_submission_logger, logger, get_errors
from mangrove.transport import Request, TransportInfo
from mangrove.transport.player.new_players import XFormPlayerV2
from mangrove.transport.repository.survey_responses import get_survey_response_by_id
from mangrove.utils.dates import py_datetime_to_js_datestring


class XFormWebSubmissionHandler():

    def __init__(self, request_user, request):
        self.request = request
        self.manager = get_database_manager(request_user)
        self.request_user = request_user
        self.player = XFormPlayerV2(self.manager, get_feeds_database(self.request_user))
        self.xml_submission_file = request.POST['form_data']
        self.media_file = {}
        if request.POST.get('media_data'):
            self.media_file.update(json.loads(request.POST['media_data']))

        self.user_profile = NGOUserProfile.objects.get(user=self.request_user)
        self.mangrove_request = Request(message=self.xml_submission_file, media=self.media_file,
            transportInfo=
            TransportInfo(transport=SMART_PHONE,
                source=self.request_user.email,
                destination=''
            ))
        self.organization = Organization.objects.get(org_id=self.user_profile.org_id)

    def create_new_submission_response(self):
        player_response = self.player.add_survey_response(self.mangrove_request, self.user_profile.reporter_id ,logger=sp_submission_logger)
        return self._post_save(player_response)

    def update_submission_response(self, survey_response_id):
        survey_response = get_survey_response_by_id(self.manager, survey_response_id)
        if not survey_response:
            raise LookupError()

        player_response = self.player.update_survey_response(self.mangrove_request, self.user_profile.reporter_id,
                                                      logger=sp_submission_logger, survey_response=survey_response)
        return self._post_save(player_response)

    def _post_save(self, response):
        mail_feed_errors(response, self.manager.database_name)
        if response.errors:
            logger.error("Error in submission : \n%s" % get_errors(response.errors))
            return HttpResponseBadRequest()

        self.organization.increment_message_count_for(incoming_sp_count=1)
        content = json.dumps({'submission_uuid':response.survey_response_id,
                              'version': response.version,
                              'created':py_datetime_to_js_datestring(response.created)})
        success_response = HttpResponse(content, status=201)
        success_response['submission_id'] = response.survey_response_id
        check_quotas_and_update_users(self.organization)
        return success_response