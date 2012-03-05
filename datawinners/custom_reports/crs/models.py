from django.db import models

# Create your models here.


class WayBillSent(models.Model):
    pl_code=models.TextField()
    waybill_code=models.TextField()
    sent_date=models.DateField()
    transaction_type=models.TextField()
    site_code=models.TextField()
    sender_name=models.TextField()
    truck_id=models.TextField()
    food_type=models.TextField()
    weight=models.IntegerField()

class WayBillReceived(models.Model):
    pl_code=models.TextField()
    waybill_code=models.TextField()
    site_code=models.TextField()
    receiver_name=models.TextField()
    received_date = models.DateField()
    truck_id=models.TextField()
    good_net_weight=models.IntegerField()
    damaged_net_weight=models.IntegerField()
