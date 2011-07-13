from django.db import models

class DatawinnerLog(models.Model):
    message = models.CharField(max_length=100)
    from_number = models.CharField(max_length=15)
    to_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    form_code = models.CharField(max_length=20, blank=True, null=True)