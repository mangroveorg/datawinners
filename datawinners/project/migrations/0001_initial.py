# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Reminder'
        db.create_table('project_reminder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project_id', self.gf('django.db.models.fields.CharField')(max_length=264)),
            ('day_of_the_month', self.gf('django.db.models.fields.IntegerField')()),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accountmanagement.Organization'])),
        ))
        db.send_create_signal('project', ['Reminder'])


    def backwards(self, orm):
        
        # Deleting model 'Reminder'
        db.delete_table('project_reminder')


    models = {
        'accountmanagement.organization': {
            'Meta': {'object_name': 'Organization'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'addressline2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.TextField', [], {}),
            'country': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'office_phone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'org_id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'sector': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'website': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'zipcode': ('django.db.models.fields.TextField', [], {})
        },
        'project.reminder': {
            'Meta': {'object_name': 'Reminder'},
            'day_of_the_month': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']"}),
            'project_id': ('django.db.models.fields.CharField', [], {'max_length': '264'})
        }
    }

    complete_apps = ['project']
