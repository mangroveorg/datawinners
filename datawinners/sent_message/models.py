from django.db import models

class PollInfo(models.Model):
    org_id = models.TextField()
    sent_on = models.DateTimeField()
    message = models.TextField()
    recipients = models.TextField()
    sender = models.TextField()
    questionnaire_id = models.TextField()


