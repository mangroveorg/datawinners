# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.scheduler.vumiclient import VumiClient, Connection
from mangrove.utils.types import is_not_empty

class SMSClient(object):

    def send_sms(self,from_tel,to_tel, message):
        if is_not_empty(from_tel):
            smsc = OrganizationSetting.objects.filter(sms_tel_number = from_tel)[0].smsc
            if smsc is not None:
                client = VumiClient(None, None, connection=Connection(smsc.vumi_username, smsc.vumi_username, base_url=settings.VUMI_API_URL))
#        The encoding of the message to utf-8 is temporary and the fix should ideally be in vumi client.
                client.send_sms(to_msisdn=to_tel,from_msisdn=from_tel, message=message.encode('utf-8'))
                return True
        return False
