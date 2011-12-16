# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LocationLevel'
        db.create_table('location_locationlevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name_0', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('name_1', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('name_2', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('name_3', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('name_4', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('location', ['LocationLevel'])


    def backwards(self, orm):
        
        # Deleting model 'LocationLevel'
        db.delete_table('location_locationlevel')


    models = {
        'location.locationlevel': {
            'Meta': {'object_name': 'LocationLevel'},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_0': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'name_1': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'name_2': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'name_3': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'name_4': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['location']
