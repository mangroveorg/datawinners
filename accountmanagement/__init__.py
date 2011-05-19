# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from registration.signals import user_registered
from datawinners.accountmanagement.post_registration_events import ngo_user_created, create_org_database

user_registered.connect(ngo_user_created)
user_registered.connect(create_org_database)