# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.execute("INSERT INTO auth_group (name) VALUES ('No Delete PM')")

    def backwards(self, orm):
        pass

    complete_apps = ['accountmanagement']

