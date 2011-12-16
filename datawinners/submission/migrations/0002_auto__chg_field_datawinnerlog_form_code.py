# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'DatawinnerLog.form_code'
        db.alter_column('submission_datawinnerlog', 'form_code', self.gf('django.db.models.fields.TextField')())


    def backwards(self, orm):
        
        # Changing field 'DatawinnerLog.form_code'
        db.alter_column('submission_datawinnerlog', 'form_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))


    models = {
        'submission.datawinnerlog': {
            'Meta': {'object_name': 'DatawinnerLog'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {}),
            'form_code': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'from_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'to_number': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['submission']
