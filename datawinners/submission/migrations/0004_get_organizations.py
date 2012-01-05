# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """Write your forwards methods here."""
        from datawinners.submission.organization_finder import OrganizationFinder

        for datawinner_log in orm.DatawinnerLog.objects.all():
            organization, error = OrganizationFinder().find(datawinner_log.from_number, datawinner_log.to_number)
            if error is None:
                datawinner_log.organization = organization
            datawinner_log.save()


    def backwards(self, orm):
        """Write your backwards methods here."""

    models = {
        'accountmanagement.organization': {
            'Meta': {'object_name': 'Organization'},
            'active_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'addressline2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.TextField', [], {}),
            'country': ('django.db.models.fields.TextField', [], {}),
            'in_trial_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deactivate_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'office_phone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'org_id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'sector': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'website': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'zipcode': ('django.db.models.fields.TextField', [], {})
        },
        'submission.datawinnerlog': {
            'Meta': {'object_name': 'DatawinnerLog'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.TextField', [], {}),
            'form_code': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'from_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']", 'null': 'True'}),
            'to_number': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['submission']
