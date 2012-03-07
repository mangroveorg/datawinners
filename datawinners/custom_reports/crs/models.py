from django.db import models


def waybillsent_handler(submission_data):
    _save_submission_via_model(submission_data,WayBillSent)


def waybillreceived_handler(submission_data):
    _save_submission_via_model(submission_data,WayBillReceived)


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

def _convert_submission_data_to_model_fields(fields=None, submission_data=None):
    fields_name = [field.name for field in fields if field.name != 'id']
    submission_values = submission_data.itervalues()
    return {field_name: submission_values.next() for field_name in fields_name}


def _save_submission_via_model(submission_data,model):
    model_fields = model._meta.fields
    submission_values = _convert_submission_data_to_model_fields(fields=model_fields,
        submission_data=submission_data)
    model(**submission_values).save()
