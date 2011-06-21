# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.db import models
from django.template.defaultfilters import slugify
from registration.models import RegistrationProfile
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator


class Organization(models.Model):
    name = models.TextField()
    sector = models.TextField()
    addressline1 = models.TextField()
    addressline2 = models.TextField(blank=True)
    city = models.TextField()
    state = models.TextField(blank=True)
    country = models.TextField()
    zipcode = models.TextField()
    office_phone = models.TextField(blank=True)
    website = models.TextField(blank=True)
    org_id = models.TextField(primary_key=True)


class NGOUserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    title = models.TextField()
    org_id = models.TextField()


class OrganizationSetting(models.Model):
    organization = models.ForeignKey(Organization, unique=True)
    document_store = models.TextField()
    sms_tel_number = models.TextField(unique=True, null=True)
    def __unicode__(self):
        return self.organization.name




def create_organization(org_details):
    organization = Organization(name=org_details.get('organization_name'),
                                sector=org_details.get('organization_sector'),
                                addressline1=org_details.get('organization_addressline1'),
                                addressline2=org_details.get('organization_addressline2'),
                                city=org_details.get('organization_city'),
                                state=org_details.get('organization_state'),
                                country=org_details.get('organization_country'),
                                zipcode=org_details.get('organization_zipcode'),
                                office_phone=org_details.get('organization_office_phone'),
                                website=org_details.get('organization_website'),
                                org_id=OrganizationIdCreator().generateId()
    )
    organization.save()
    organization_setting = OrganizationSetting()
    organization_setting.organization = organization
    organization_setting.document_store = slugify("%s_%s_%s" % ("HNI", organization.name, organization.org_id))
    organization_setting.save()
    return organization
