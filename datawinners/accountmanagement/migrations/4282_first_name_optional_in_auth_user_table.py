# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        db.execute("ALTER TABLE auth_user ALTER COLUMN first_name DROP NOT NULL")
        db.execute("ALTER TABLE auth_user ALTER COLUMN last_name DROP NOT NULL")

    def backwards(self, orm):
        
        db.execute("ALTER TABLE auth_user ALTER COLUMN first_name SET NOT NULL")
        db.execute("ALTER TABLE auth_user ALTER COLUMN last_name SET NOT NULL")

    complete_apps = ['django.contrib.auth']
