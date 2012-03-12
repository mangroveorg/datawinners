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
            ('q1', self.gf('django.db.models.fields.TextField')(db_column='pl_code')),
            ('q2', self.gf('django.db.models.fields.TextField')(db_column='waybill_code')),
            ('q3', self.gf('django.db.models.fields.TextField')(db_column='sent_date')),
            ('q4', self.gf('django.db.models.fields.TextField')(db_column='transaction_type')),
            ('q5', self.gf('django.db.models.fields.TextField')(db_column='site_code')),
            ('q6', self.gf('django.db.models.fields.TextField')(db_column='sender_name')),
            ('q7', self.gf('django.db.models.fields.TextField')(db_column='truck_id')),
            ('q8', self.gf('django.db.models.fields.TextField')(db_column='food_type')),
            ('q9', self.gf('django.db.models.fields.IntegerField')(db_column='weight')),
        ))
        db.send_create_signal('crs', ['WayBillSent'])

        # Adding model 'WayBillReceived'
        db.create_table('crs_waybillreceived', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('q1', self.gf('django.db.models.fields.TextField')(db_column='pl_code')),
            ('q2', self.gf('django.db.models.fields.TextField')(db_column='waybill_code')),
            ('q3', self.gf('django.db.models.fields.TextField')(db_column='site_code')),
            ('q4', self.gf('django.db.models.fields.TextField')(db_column='receiver_name')),
            ('q5', self.gf('django.db.models.fields.TextField')(db_column='received_date')),
            ('q6', self.gf('django.db.models.fields.TextField')(db_column='truck_id')),
            ('q7', self.gf('django.db.models.fields.IntegerField')(db_column='good_net_weight')),
            ('q8', self.gf('django.db.models.fields.IntegerField')(db_column='damaged_net_weight')),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'receiver_name'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'received_date'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'truck_id'"}),
            'q7': ('django.db.models.fields.IntegerField', [], {'db_column': "'good_net_weight'"}),
            'q8': ('django.db.models.fields.IntegerField', [], {'db_column': "'damaged_net_weight'"})
        },
        'crs.waybillsent': {
            'Meta': {'object_name': 'WayBillSent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'sent_date'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'transaction_type'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'sender_name'"}),
            'q7': ('django.db.models.fields.TextField', [], {'db_column': "'truck_id'"}),
            'q8': ('django.db.models.fields.TextField', [], {'db_column': "'food_type'"}),
            'q9': ('django.db.models.fields.IntegerField', [], {'db_column': "'weight'"})
        }
    }

    complete_apps = ['crs']
