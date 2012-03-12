from django.db import models


def waybillsent_handler(submission_data):
    _save_submission_via_model(submission_data, WayBillSent)


def waybillreceived_handler(submission_data):
    _save_submission_via_model(submission_data, WayBillReceived)


class WayBillSent(models.Model):
    q1 = models.TextField(db_column='pl_code')
    q2 = models.TextField(db_column='waybill_code')
    q3 = models.TextField(db_column='sent_date')
    q4 = models.TextField(db_column='transaction_type')
    q5 = models.TextField(db_column='site_code')
    q6 = models.TextField(db_column='sender_name')
    q7 = models.TextField(db_column='truck_id')
    q8 = models.TextField(db_column='food_type')
    q9 = models.IntegerField(db_column='weight')


class WayBillReceived(models.Model):
    q1 = models.TextField(db_column='pl_code')
    q2 = models.TextField(db_column='waybill_code')
    q3 = models.TextField(db_column='site_code')
    q4 = models.TextField(db_column='receiver_name')
    q5 = models.TextField(db_column='received_date')
    q6 = models.TextField(db_column='truck_id')
    q7 = models.IntegerField(db_column='good_net_weight')
    q8 = models.IntegerField(db_column='damaged_net_weight')


def _convert_submission_data_to_model_fields(fields=None, submission_data=None):
    field_names = [field.name for field in fields if field.name != 'id']
    return  {field_name: submission_data.get(field_name) for field_name in field_names}


def _save_submission_via_model(submission_data, model):
    model_fields = model._meta.fields
    submission_values = _convert_submission_data_to_model_fields(fields=model_fields,
        submission_data=submission_data)
    model(**submission_values).save()
