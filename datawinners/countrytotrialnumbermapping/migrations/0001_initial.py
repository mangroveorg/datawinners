# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Country'
        db.create_table('countrytotrialnumbermapping_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country_name', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('country_code', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('countrytotrialnumbermapping', ['Country'])


    def backwards(self, orm):
        
        # Deleting model 'Country'
        db.delete_table('countrytotrialnumbermapping_country')


    models = {
        'countrytotrialnumbermapping.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.TextField', [], {}),
            'country_name': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['countrytotrialnumbermapping']
