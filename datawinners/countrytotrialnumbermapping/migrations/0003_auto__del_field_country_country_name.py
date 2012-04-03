# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Country.country_name'
        db.delete_column('countrytotrialnumbermapping_country', 'country_name')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Country.country_name'
        raise RuntimeError("Cannot reverse this migration. 'Country.country_name' and its values cannot be restored.")


    models = {
        'countrytotrialnumbermapping.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.TextField', [], {}),
            'country_name_en': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True'}),
            'country_name_fr': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'countrytotrialnumbermapping.network': {
            'Meta': {'object_name': 'Network'},
            'country': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['countrytotrialnumbermapping.Country']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network_name': ('django.db.models.fields.TextField', [], {}),
            'trial_sms_number': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['countrytotrialnumbermapping']
