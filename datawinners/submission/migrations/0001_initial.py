# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DatawinnerLog'
        db.create_table('submission_datawinnerlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('from_number', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('to_number', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('form_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('error', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('submission', ['DatawinnerLog'])


    def backwards(self, orm):
        
        # Deleting model 'DatawinnerLog'
        db.delete_table('submission_datawinnerlog')


    models = {
        'submission.datawinnerlog': {
            'Meta': {'object_name': 'DatawinnerLog'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {}),
            'form_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'from_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'to_number': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['submission']
