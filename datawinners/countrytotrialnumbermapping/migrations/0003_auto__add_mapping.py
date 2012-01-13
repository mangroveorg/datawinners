# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Mapping'
        db.create_table('countrytotrialnumbermapping_mapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countrytotrialnumbermapping.Country'])),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countrytotrialnumbermapping.Network'])),
        ))
        db.send_create_signal('countrytotrialnumbermapping', ['Mapping'])


    def backwards(self, orm):
        
        # Deleting model 'Mapping'
        db.delete_table('countrytotrialnumbermapping_mapping')


    models = {
        'countrytotrialnumbermapping.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.TextField', [], {}),
            'country_name': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'countrytotrialnumbermapping.mapping': {
            'Meta': {'object_name': 'Mapping'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countrytotrialnumbermapping.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countrytotrialnumbermapping.Network']"})
        },
        'countrytotrialnumbermapping.network': {
            'Meta': {'object_name': 'Network'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network_name': ('django.db.models.fields.TextField', [], {}),
            'trial_sms_number': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['countrytotrialnumbermapping']
