from django.contrib.auth.models import User, UserManager
from django.db import models

# Create your models here.
class   Organization(models.Model):
    name = models.TextField()
    sector = models.TextField()
    addressline1 = models.TextField()
    addressline2 = models.TextField()
    city = models.TextField()
    state = models.TextField()
    country = models.TextField()
    zipcode = models.TextField()
    office_phone = models.TextField()
    website = models.TextField()
    org_id=models.TextField()
#    models.ManyToOneRel(User,'id')
#    administrators = models.ForeignKey(User)

class NGOUser(User):
    title = models.TextField()
#    organization=models.ForeignKey(Organization)

   # Use UserManager to get the create_user method, etc.
    objects = UserManager()

