# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners import settings
from datawinners.scheduler.vumiclient import VumiClient, Connection

class SMSClient(object):
    def __init__(self):
        self.client = VumiClient(None, None, connection=Connection(settings.VUMI_USER, settings.VUMI_PASSWORD, base_url=settings.VUMI_API_URL))

    def send_sms(self,from_tel,to_tel, message):
        self.client.send_sms(to_msisdn=to_tel,from_msisdn=from_tel, message=message.encode('utf-8'))