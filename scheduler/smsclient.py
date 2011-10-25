# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
import logging
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.scheduler.vumiclient import VumiClient, Connection
from mangrove.utils.types import is_not_empty
logger = logging.getLogger("datawinners.reminders")

class SMSClient(object):

    def send_sms(self,from_tel,to_tel, message):
        if is_not_empty(from_tel):
            smsc = OrganizationSetting.objects.filter(sms_tel_number = from_tel)[0].smsc
            if smsc is not None:
                client = VumiClient(None, None, connection=Connection(smsc.vumi_username, smsc.vumi_username, base_url=settings.VUMI_API_URL))
                client.send_sms(to_msisdn=to_tel,from_msisdn=from_tel, message=message.encode('utf-8'))
                return True
        return False

    def send_reminder(self,from_number, on_date, project, reminder, dbm):
        count = 0
        for data_sender in reminder.get_sender_list(project, on_date,dbm):
            sms_sent = self.send_sms(from_number, data_sender["mobile_number"], reminder.message)
            if sms_sent:
                count += 1
            logger.info("Reminder sent for %s, Message: %s" % (data_sender["mobile_number"],reminder.message,) )
        return count

