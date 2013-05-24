import json
import logging
from django.conf import settings
from datawinners.feeds.database import get_feeds_db_for_org
from mangrove.transport import TransportInfo
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER, OrganizationSetting
from datawinners.messageprovider.messages import SMS
from datawinners.utils import get_organization, get_database_manager_for_org

logger = logging.getLogger("django")

class WebSMSDBMRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['dbm']=get_database_manager_for_org(mangrove_request['organization'])
        mangrove_request['feeds_dbm'] = get_feeds_db_for_org(mangrove_request['organization'])


class WebSMSTransportInfoRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        organization_settings = OrganizationSetting.objects.get(organization=mangrove_request['organization'])
        _to = get_organization_number(organization_settings.get_organisation_sms_number()[0])
        _from = TEST_REPORTER_MOBILE_NUMBER

        mangrove_request['transport_info']=TransportInfo(SMS, _from, _to)

class WebSMSOrganizationFinderRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['organization'] = get_organization(http_request)

class SMSMessageRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        if settings.USE_NEW_VUMI:
            data = http_request.raw_post_data
            params = json.loads(data)
            message_ = params['content']
        else:
            message_ = http_request.POST['message']
        mangrove_request['incoming_message']= message_

class SMSTransportInfoRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        vumi_parameters = get_vumi_parameters(http_request)
        mangrove_request['transport_info']=TransportInfo(SMS, vumi_parameters.from_number,
            vumi_parameters.to_number)

class MangroveWebSMSRequestProcessor(object):
    middlewares=[SMSMessageRequestProcessor(),WebSMSOrganizationFinderRequestProcessor(),WebSMSTransportInfoRequestProcessor(),WebSMSDBMRequestProcessor()]
    def process(self, http_request, mangrove_request):
        for middleware in self.middlewares:
            middleware.process(http_request,mangrove_request)

def get_organization_number(organization_number):
    return organization_number[0] if(isinstance(organization_number, list)) else organization_number


def try_get_value(request_params, key):
    return request_params[key] if request_params.has_key(key) else None


def get_vumi_parameters(http_request):
    http_request_post = http_request.POST

    if settings.USE_NEW_VUMI:
        data = http_request.raw_post_data
        logger.info('http request raw post data: %s' % data)
        params = json.loads(data)
        from_addr_ = try_get_value(params, "from_addr")
        to_addr_ = try_get_value(params, "to_addr")
        return VumiParameters(from_number=from_addr_, to_number=to_addr_, content=params["content"], is_new_vumi = True)
    else:
        from_addr_ = try_get_value(http_request_post, "from_msisdn")
        to_addr_ = try_get_value(http_request_post, "to_msisdn")
        return VumiParameters(from_number=from_addr_, to_number=to_addr_, content=http_request_post["message"], is_new_vumi=False)

class VumiParameters(object):
    def __init__(self, from_number, to_number, content, is_new_vumi):
        self.from_number = from_number
        self.to_number = to_number
        self.content = content
        self.is_new_vumi = is_new_vumi