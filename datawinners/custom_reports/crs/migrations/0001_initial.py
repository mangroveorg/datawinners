# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WayBillSent'
        db.create_table('crs_waybillsent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pl_code', self.gf('django.db.models.fields.TextField')()),
            ('waybill_code', self.gf('django.db.models.fields.TextField')()),
            ('sent_date', self.gf('django.db.models.fields.DateField')()),
            ('transaction_type', self.gf('django.db.models.fields.TextField')()),
            ('site_code', self.gf('django.db.models.fields.TextField')()),
            ('sender_name', self.gf('django.db.models.fields.TextField')()),
            ('truck_id', self.gf('django.db.models.fields.TextField')()),
            ('food_type', self.gf('django.db.models.fields.TextField')()),
            ('weight', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('crs', ['WayBillSent'])

        # Adding model 'WayBillReceived'
        db.create_table('crs_waybillreceived', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pl_code', self.gf('django.db.models.fields.TextField')()),
            ('waybill_code', self.gf('django.db.models.fields.TextField')()),
            ('site_code', self.gf('django.db.models.fields.TextField')()),
            ('receiver_name', self.gf('django.db.models.fields.TextField')()),
            ('received_date', self.gf('django.db.models.fields.DateField')()),
            ('truck_id', self.gf('django.db.models.fields.TextField')()),
            ('good_net_weight', self.gf('django.db.models.fields.IntegerField')()),
            ('damaged_net_weight', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('crs', ['WayBillReceived'])


    def backwards(self, orm):
        
        # Deleting model 'WayBillSent'
        db.delete_table('crs_waybillsent')

        # Deleting model 'WayBillReceived'
        db.delete_table('crs_waybillreceived')


    models = {
        'crs.waybillreceived': {
            'Meta': {'object_name': 'WayBillReceived'},
            'damaged_net_weight': ('django.db.models.fields.IntegerField', [], {}),
            'good_net_weight': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pl_code': ('django.db.models.fields.TextField', [], {}),
            'received_date': ('django.db.models.fields.DateField', [], {}),
            'receiver_name': ('django.db.models.fields.TextField', [], {}),
            'site_code': ('django.db.models.fields.TextField', [], {}),
            'truck_id': ('django.db.models.fields.TextField', [], {}),
            'waybill_code': ('django.db.models.fields.TextField', [], {})
        },
        'crs.waybillsent': {
            'Meta': {'object_name': 'WayBillSent'},
            'food_type': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pl_code': ('django.db.models.fields.TextField', [], {}),
            'sender_name': ('django.db.models.fields.TextField', [], {}),
            'sent_date': ('django.db.models.fields.DateField', [], {}),
            'site_code': ('django.db.models.fields.TextField', [], {}),
            'transaction_type': ('django.db.models.fields.TextField', [], {}),
            'truck_id': ('django.db.models.fields.TextField', [], {}),
            'waybill_code': ('django.db.models.fields.TextField', [], {}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['crs']
