import datetime
from django.db import models

class OutgoingMessage(models.Model):
    from_msisdn = models.TextField()
    to_msisdn = models.TextField()
    message = models.TextField()
    sent_date = models.DateTimeField(default=datetime.datetime.now)



