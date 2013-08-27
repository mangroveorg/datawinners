# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from mangrove.utils.types import is_empty

class Migration(DataMigration):

    def forwards(self, orm):
        for org in orm.Organization.objects.all():
            if not org.status:
                status = 'Activated'
                status_changed_datetime = datetime.datetime.now() if is_empty(org.active_date) else org.active_date
                org.status_changed_datetime = status_changed_datetime
                org.status = status
                org.save()


    def backwards(self, orm):
        pass


    models = {
        'accountmanagement.datasenderontrialaccount': {
            'Meta': {'object_name': 'DataSenderOnTrialAccount'},
            'mobile_number': ('django.db.models.fields.TextField', [], {'unique': 'True', 'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']"})
        },
        'accountmanagement.messagetracker': {
            'Meta': {'object_name': 'MessageTracker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incoming_sms_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'month': ('django.db.models.fields.DateField', [], {}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']"}),
            'outgoing_sms_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sms_api_usage_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'accountmanagement.ngouserprofile': {
            'Meta': {'object_name': 'NGOUserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_phone': ('django.db.models.fields.TextField', [], {}),
            'org_id': ('django.db.models.fields.TextField', [], {}),
            'reporter_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'accountmanagement.organization': {
            'Meta': {'object_name': 'Organization'},
            'active_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'addressline2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.TextField', [], {}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'in_trial_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deactivate_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'office_phone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'org_id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'sector': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'status_changed_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'zipcode': ('django.db.models.fields.TextField', [], {})
        },
        'accountmanagement.organizationsetting': {
            'Meta': {'object_name': 'OrganizationSetting'},
            'document_store': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']", 'unique': 'True'}),
            'outgoing_number': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.OutgoingNumberSetting']", 'null': 'True'}),
            'sms_tel_number': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True'})
        },
        'accountmanagement.outgoingnumbersetting': {
            'Meta': {'object_name': 'OutgoingNumberSetting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'smsc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.SMSC']", 'null': 'True'})
        },
        'accountmanagement.paymentdetails': {
            'Meta': {'object_name': 'PaymentDetails'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_period': ('django.db.models.fields.TextField', [], {}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accountmanagement.Organization']"}),
            'preferred_payment': ('django.db.models.fields.TextField', [], {})
        },
        'accountmanagement.smsc': {
            'Meta': {'object_name': 'SMSC'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vumi_username': ('django.db.models.fields.TextField', [], {})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accountmanagement']
