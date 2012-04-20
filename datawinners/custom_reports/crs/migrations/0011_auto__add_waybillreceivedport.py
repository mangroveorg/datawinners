# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WayBillReceivedPort'
        db.create_table('crs_waybillreceivedport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('q1', self.gf('django.db.models.fields.TextField')(db_column='waybill_code')),
            ('q2', self.gf('django.db.models.fields.DateField')(db_column='received_date')),
            ('q3', self.gf('django.db.models.fields.FloatField')(db_column='good_weight')),
            ('q4', self.gf('django.db.models.fields.FloatField')(db_column='damaged_weight')),
        ))
        db.send_create_signal('crs', ['WayBillReceivedPort'])


    def backwards(self, orm):
        
        # Deleting model 'WayBillReceivedPort'
        db.delete_table('crs_waybillreceivedport')


    models = {
        'crs.billoflading': {
            'Meta': {'object_name': 'BillOfLading'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'shipment_type'"}),
            'q3': ('django.db.models.fields.DateField', [], {'db_column': "'issue_date'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'food_type'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'bill_of_lading_code'"}),
            'q6': ('django.db.models.fields.FloatField', [], {'db_column': "'weight'"})
        },
        'crs.breakbulksent': {
            'Meta': {'object_name': 'BreakBulkSent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.DateField', [], {'db_column': "'sent_date'"}),
            'q2': ('django.db.models.fields.FloatField', [], {'db_column': "'weight'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"})
        },
        'crs.distribution': {
            'Meta': {'object_name': 'Distribution'},
            'distribution_type': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"}),
            'q2': ('django.db.models.fields.DateField', [], {'db_column': "'distribution_date'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'received_waybill_code'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'returned_waybill_code'"}),
            'q5': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'oil'"}),
            'q6': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'csb'"}),
            'q7': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'sorghum'"}),
            'q8': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'rice'"})
        },
        'crs.physicalinventorysheet': {
            'Meta': {'object_name': 'PhysicalInventorySheet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'store_house_code'"}),
            'q2': ('django.db.models.fields.DateField', [], {'db_column': "'physical_inventory_closing_date'"}),
            'q3': ('django.db.models.fields.DateField', [], {'db_column': "'actual_physical_inventory_date'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'food_type'"}),
            'q6': ('django.db.models.fields.FloatField', [], {'db_column': "'good_net_weight'"}),
            'q7': ('django.db.models.fields.FloatField', [], {'db_column': "'damaged_net_weight'"})
        },
        'crs.siteactivities': {
            'Meta': {'object_name': 'SiteActivities'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'fiscal_year_with_initials'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'site_location'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'site_gps_coordinates'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'tel_no'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'site_person_responsible'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'type_of_activity'"}),
            'q7': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"})
        },
        'crs.warehouse': {
            'Meta': {'object_name': 'Warehouse'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'name'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'address'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'gps_coordinates'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'tel_no'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'initials'"})
        },
        'crs.waybillreceived': {
            'Meta': {'object_name': 'WayBillReceived'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'receiver_name'"}),
            'q5': ('django.db.models.fields.DateField', [], {'db_column': "'received_date'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'truck_id'"}),
            'q7': ('django.db.models.fields.FloatField', [], {'db_column': "'good_net_weight'"}),
            'q8': ('django.db.models.fields.FloatField', [], {'db_column': "'damaged_net_weight'"}),
            'q9': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'transaction_type'"})
        },
        'crs.waybillreceivedport': {
            'Meta': {'object_name': 'WayBillReceivedPort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q2': ('django.db.models.fields.DateField', [], {'db_column': "'received_date'"}),
            'q3': ('django.db.models.fields.FloatField', [], {'db_column': "'good_weight'"}),
            'q4': ('django.db.models.fields.FloatField', [], {'db_column': "'damaged_weight'"})
        },
        'crs.waybillsent': {
            'Meta': {'object_name': 'WayBillSent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q10': ('django.db.models.fields.TextField', [], {'db_column': "'receiver_code'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q3': ('django.db.models.fields.DateField', [], {'db_column': "'sent_date'"}),
            'q4': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'transaction_type'"}),
            'q5': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'warehouse_code'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'sender_name'"}),
            'q7': ('django.db.models.fields.TextField', [], {'db_column': "'truck_id'"}),
            'q8': ('django.db.models.fields.TextField', [], {'db_column': "'food_type'"}),
            'q9': ('django.db.models.fields.FloatField', [], {'db_column': "'weight'"})
        }
    }

    complete_apps = ['crs']
