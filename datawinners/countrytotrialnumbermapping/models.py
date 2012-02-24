from django.db import models

class Country(models.Model):
    country_name = models.TextField(unique=True)
    country_code = models.TextField()

    def __unicode__(self):
        return self.country_name


class Network(models.Model):
    network_name = models.TextField()
    trial_sms_number = models.TextField()
    country=models.ManyToManyField(Country)
