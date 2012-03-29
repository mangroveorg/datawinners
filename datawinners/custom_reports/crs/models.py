from django.db import models


def crs_model_creator(submission_data, model):
    _save_submission_via_model(submission_data, model)

class WayBillSent(models.Model):
    q1 = models.TextField(db_column='pl_code')
    q2 = models.TextField(db_column='waybill_code')
    q3 = models.DateField(db_column='sent_date')
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
    q5 = models.DateField(db_column='received_date')
    q6 = models.TextField(db_column='truck_id')
    q7 = models.IntegerField(db_column='good_net_weight')
    q8 = models.IntegerField(db_column='damaged_net_weight')


class SFMDistribution(models.Model):
    q1 = models.TextField(db_column='site_code')
    q2 = models.DateField(db_column='distribution_date')
    q3 = models.TextField(db_column='received_waybill_code')
    q4 = models.IntegerField(db_column='distributed_oil_quantity')
    q5 = models.IntegerField(db_column='distributed_csb_quantity')
    q6 = models.TextField(db_column='returned_waybill_code')
    q7 = models.IntegerField(db_column='returned_oil_quantity')
    q8 = models.IntegerField(db_column='returned_csb_quantity')


class PhysicalInventorySheet(models.Model):
    q1 = models.TextField(db_column='store_house_code')
    q2 = models.DateField(db_column='physical_inventory_closing_date')
    q3 = models.DateField(db_column='actual_physical_inventory_date')
    q4 = models.TextField(db_column='pl_code')
    q5 = models.TextField(db_column='food_type')
    q6 = models.IntegerField(db_column='good_net_weight')
    q7 = models.IntegerField(db_column='damaged_net_weight')


class SiteActivities(models.Model):
    q1 = models.TextField(db_column='fiscal_year_with_initials')
    q2 = models.TextField(db_column='site_location')
    q3 = models.TextField(db_column='site_gps_coordinates')
    q4 = models.TextField(db_column='tel_no')
    q5 = models.TextField(db_column='site_person_responsible')
    q6 = models.TextField(db_column='type_of_activity')
    q7 = models.TextField(db_column='site_code')


class Warehouse(models.Model):
    q1 = models.TextField(db_column='name')
    q2 = models.TextField(db_column='address')
    q3 = models.TextField(db_column='gps_coordinates')
    q4 = models.TextField(db_column='tel_no')
    q5 = models.TextField(db_column='initials')


def _convert_submission_data_to_model_fields(fields=None, submission_data=None):
    field_names = [field.name for field in fields if field.name != 'id']
    return  {field_name: submission_data.get(field_name) for field_name in field_names}


def _save_submission_via_model(submission_data, model):
    model_fields = model._meta.fields
    submission_values = _convert_submission_data_to_model_fields(fields=model_fields,
        submission_data=submission_data)
    model(**submission_values).save()
