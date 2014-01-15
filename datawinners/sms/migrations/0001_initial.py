# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SMS'
        db.create_table('sms_sms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accountmanagement.Organization'])),
            ('created_at', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('delivered_at', self.gf('django.db.models.fields.DateField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('message_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('msg_from', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('msg_to', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('smsc', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('msg_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('sms', ['SMS'])


    def backwards(self, orm):
        
        # Deleting model 'SMS'
        db.delete_table('sms_sms')


    models = {
        'accountmanagement.organization': {
            'Meta': {'object_name': 'Organization'},
            'account_type': ('django.db.models.fields.CharField', [], {'default': "'Pro SMS'", 'max_length': '20', 'null': 'True'}),
            'active_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'addressline2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.TextField', [], {}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'is_deactivate_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2', 'null': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'office_phone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'org_id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'sector': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Activated'", 'max_length': '20', 'null': 'True'}),
            'status_changed_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'zipcode': ('django.db.models.fields.TextField', [], {})
        },
        'sms.sms': {
            'Meta': {'object_name': 'SMS'},
            'created_at': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delivered_at': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'msg_from': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'msg_to': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'msg_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']"}),
            'smsc': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['sms']
