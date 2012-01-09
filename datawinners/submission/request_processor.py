from mangrove.transport import TransportInfo
from accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER, OrganizationSetting
from messageprovider.messages import SMS
from utils import get_organization, get_database_manager_for_org

class WebSMSDBMRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['dbm']=get_database_manager_for_org(mangrove_request['organization'])


class WebSMSTransportInfoRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        organization_settings = OrganizationSetting.objects.get(organization=mangrove_request['organization'])
        _to = organization_settings.get_organisation_sms_number()
        _from = TEST_REPORTER_MOBILE_NUMBER

        mangrove_request['transport_info']=TransportInfo(SMS, _from, _to)

class WebSMSOrganizationFinderRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['organization'] = get_organization(http_request)

class SMSMessageRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['incoming_message']=http_request.POST['message']

class SMSTransportInfoRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['transport_info']=TransportInfo(SMS, http_request.POST["from_msisdn"],
            http_request.POST["to_msisdn"])

class MangroveWebSMSRequestProcessor(object):
    middlewares=[SMSMessageRequestProcessor(),WebSMSOrganizationFinderRequestProcessor(),WebSMSTransportInfoRequestProcessor(),WebSMSDBMRequestProcessor()]
    def process(self, http_request, mangrove_request):
        for middleware in self.middlewares:
            middleware.process(http_request,mangrove_request)

