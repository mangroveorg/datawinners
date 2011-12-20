from mangrove.transport import TransportInfo
from accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from main.utils import get_database_manager
from messageprovider.messages import SMS
from utils import get_organization_settings_from_request

class WebSMSDBMRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        mangrove_request['dbm']=get_database_manager(http_request.user)


class WebSMSTransportInfoRequestProcessor(object):
    def process(self, http_request, mangrove_request):
        _to = get_organization_settings_from_request(http_request).get_organisation_sms_number()
        _from = TEST_REPORTER_MOBILE_NUMBER

        mangrove_request['transport_info']=TransportInfo(SMS, _from, _to)
