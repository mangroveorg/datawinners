# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Country.country_name_en'
        db.add_column('countrytotrialnumbermapping_country', 'country_name_en', self.gf('django.db.models.fields.TextField')(unique=True, null=True), keep_default=False)

        # Adding field 'Country.country_name_fr'
        db.add_column('countrytotrialnumbermapping_country', 'country_name_fr', self.gf('django.db.models.fields.TextField')(unique=True, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Country.country_name_en'
        db.delete_column('countrytotrialnumbermapping_country', 'country_name_en')

        # Deleting field 'Country.country_name_fr'
        db.delete_column('countrytotrialnumbermapping_country', 'country_name_fr')


    models = {
        'countrytotrialnumbermapping.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.TextField', [], {}),
            'country_name': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
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
