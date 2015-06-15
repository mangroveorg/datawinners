from django.contrib.auth.models import User
from django.db import models
class UserPreferences(models.Model):
    user = models.ForeignKey(User)
    preference_name = models.TextField()
    preference_value = models.BooleanField(default=False)

  