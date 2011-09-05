# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Reminder.day_of_the_month'
        db.delete_column('project_reminder', 'day_of_the_month')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Reminder.day_of_the_month'
        raise RuntimeError("Cannot reverse this migration. 'Reminder.day_of_the_month' and its values cannot be restored.")


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
            'day': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']"}),
            'project_id': ('django.db.models.fields.CharField', [], {'max_length': '264'}),
            'relative': ('django.db.models.fields.CharField', [], {'default': "'before'", 'max_length': '6'}),
            'reminder_mode': ('django.db.models.fields.CharField', [], {'default': "'before_deadline'", 'max_length': '20'})
        }
    }

    complete_apps = ['project']
