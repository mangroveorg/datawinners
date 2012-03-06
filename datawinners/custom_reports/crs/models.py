from django.db import models

# Create your models here.

def populate_db(django_fields=None, submission_data=None):
    waybill_fields = [field.name for field in django_fields if field.name != 'id']
    submission_values = submission_data.itervalues()
    return {field: submission_values.next() for field in waybill_fields}


def waybillsent_handler(submission_data):
    sent_django_fields = WayBillSent._meta.fields
    submission_values = populate_db(django_fields=sent_django_fields, submission_data=submission_data)
    WayBillSent(**submission_values).save()


def waybillreceived_handler(submission_data):
    received_django_fields = WayBillReceived._meta.fields
    submission_values = populate_db(django_fields=received_django_fields, submission_data=submission_data)
    WayBillReceived(**submission_values).save()


class WayBillSent(models.Model):
    pl_code = models.TextField()
    waybill_code = models.TextField()
    sent_date = models.TextField()
    transaction_type = models.TextField()
    site_code = models.TextField()
    sender_name = models.TextField()
    truck_id = models.TextField()
    food_type = models.TextField()
    weight = models.IntegerField()


class WayBillReceived(models.Model):
    pl_code = models.TextField()
    waybill_code = models.TextField()
    site_code = models.TextField()
    receiver_name = models.TextField()
    received_date = models.TextField()
    truck_id = models.TextField()
    good_net_weight = models.IntegerField()
    damaged_net_weight = models.IntegerField()
