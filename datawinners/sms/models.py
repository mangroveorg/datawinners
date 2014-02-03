from django.db import models

from datawinners.accountmanagement.models import Organization

MSG_TYPE_USER_MSG = "User Message"
MSG_TYPE_API = "API"
MSG_TYPE_REMINDER = "Reminder"
MSG_TYPE_SUBMISSION_REPLY = "Automatic Reply"

class SMS(models.Model):
    organization = models.ForeignKey(Organization)
    created_at = models.DateField(auto_now_add=True)
    delivered_at = models.DateField(null=True)
    status = models.CharField(max_length=20)
    message_id = models.CharField(max_length=32, unique=True)
    message = models.TextField()
    msg_from = models.CharField(max_length=30)
    msg_to = models.CharField(max_length=30)
    smsc = models.CharField(max_length=30)
    msg_type = models.CharField(max_length=15)

