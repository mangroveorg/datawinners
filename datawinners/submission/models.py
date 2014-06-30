from django.db import models
from datawinners.accountmanagement.models import Organization
from datawinners.messageprovider.message_handler import get_response_message

class DatawinnerLog(models.Model):
    message = models.TextField()
    from_number = models.CharField(max_length=15)
    to_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    form_code = models.TextField(
        default="") #Because if there is grabage sms which doesnt have any whitespace before 20 chars this would break
    error = models.TextField()
    organization = models.ForeignKey(Organization, null=True)


class SMSResponse(object):
    def __init__(self, response, incoming_request):
        self.response = response
        self.request = incoming_request

    def text(self, dbm):
        return get_response_message(self.response, dbm, self.request)