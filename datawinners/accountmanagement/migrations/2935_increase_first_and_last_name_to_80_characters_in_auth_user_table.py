# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        db.execute("ALTER TABLE auth_user ALTER COLUMN first_name TYPE varchar(80)")
        db.execute("ALTER TABLE auth_user ALTER COLUMN last_name TYPE varchar(80)")

    def backwards(self, orm):
        
        db.execute("ALTER TABLE auth_user ALTER COLUMN first_name TYPE varchar(30)")
        db.execute("ALTER TABLE auth_user ALTER COLUMN last_name TYPE varchar(30)")

    complete_apps = ['django.contrib.auth']
