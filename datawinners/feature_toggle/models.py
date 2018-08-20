from django.db import models
from datawinners.accountmanagement.models import Organization

class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.name

class FeatureSubscription(models.Model):
    feature = models.OneToOneField(Feature)
    organizations = models.ManyToManyField(Organization, blank=True)