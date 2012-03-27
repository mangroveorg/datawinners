# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'WayBillReceived.q5'
        db.alter_column('crs_waybillreceived', 'received_date', self.gf('django.db.models.fields.DateField')(db_column='received_date'))

        # Changing field 'SFMDistribution.q2'
        db.alter_column('crs_sfmdistribution', 'distribution_date', self.gf('django.db.models.fields.DateField')(db_column='distribution_date'))

        # Changing field 'WayBillSent.q3'
        db.alter_column('crs_waybillsent', 'sent_date', self.gf('django.db.models.fields.DateField')(db_column='sent_date'))

        # Changing field 'PhysicalInventorySheet.q3'
        db.alter_column('crs_physicalinventorysheet', 'actual_physical_inventory_date', self.gf('django.db.models.fields.DateField')(db_column='actual_physical_inventory_date'))

        # Changing field 'PhysicalInventorySheet.q2'
        db.alter_column('crs_physicalinventorysheet', 'physical_inventory_closing_date', self.gf('django.db.models.fields.DateField')(db_column='physical_inventory_closing_date'))


    def backwards(self, orm):
        
        # Changing field 'WayBillReceived.q5'
        db.alter_column('crs_waybillreceived', 'received_date', self.gf('django.db.models.fields.TextField')(db_column='received_date'))

        # Changing field 'SFMDistribution.q2'
        db.alter_column('crs_sfmdistribution', 'distribution_date', self.gf('django.db.models.fields.TextField')(db_column='distribution_date'))

        # Changing field 'WayBillSent.q3'
        db.alter_column('crs_waybillsent', 'sent_date', self.gf('django.db.models.fields.TextField')(db_column='sent_date'))

        # Changing field 'PhysicalInventorySheet.q3'
        db.alter_column('crs_physicalinventorysheet', 'actual_physical_inventory_date', self.gf('django.db.models.fields.TextField')(db_column='actual_physical_inventory_date'))

        # Changing field 'PhysicalInventorySheet.q2'
        db.alter_column('crs_physicalinventorysheet', 'physical_inventory_closing_date', self.gf('django.db.models.fields.TextField')(db_column='physical_inventory_closing_date'))


    models = {
        'crs.physicalinventorysheet': {
            'Meta': {'object_name': 'PhysicalInventorySheet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'store_house_code'"}),
            'q2': ('django.db.models.fields.DateField', [], {'db_column': "'physical_inventory_closing_date'"}),
            'q3': ('django.db.models.fields.DateField', [], {'db_column': "'actual_physical_inventory_date'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'food_type'"}),
            'q6': ('django.db.models.fields.IntegerField', [], {'db_column': "'good_net_weight'"}),
            'q7': ('django.db.models.fields.IntegerField', [], {'db_column': "'damaged_net_weight'"})
        },
        'crs.sfmdistribution': {
            'Meta': {'object_name': 'SFMDistribution'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"}),
            'q2': ('django.db.models.fields.DateField', [], {'db_column': "'distribution_date'"}),
            'q3': ('django.db.models.fields.TextField', [], {'db_column': "'received_waybill_code'"}),
            'q4': ('django.db.models.fields.IntegerField', [], {'db_column': "'distributed_oil_quantity'"}),
            'q5': ('django.db.models.fields.IntegerField', [], {'db_column': "'distributed_csb_quantity'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'returned_waybill_code'"}),
            'q7': ('django.db.models.fields.IntegerField', [], {'db_column': "'returned_oil_quantity'"}),
            'q8': ('django.db.models.fields.IntegerField', [], {'db_column': "'returned_csb_quantity'"})
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
            'q7': ('django.db.models.fields.IntegerField', [], {'db_column': "'good_net_weight'"}),
            'q8': ('django.db.models.fields.IntegerField', [], {'db_column': "'damaged_net_weight'"})
        },
        'crs.waybillsent': {
            'Meta': {'object_name': 'WayBillSent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q1': ('django.db.models.fields.TextField', [], {'db_column': "'pl_code'"}),
            'q2': ('django.db.models.fields.TextField', [], {'db_column': "'waybill_code'"}),
            'q3': ('django.db.models.fields.DateField', [], {'db_column': "'sent_date'"}),
            'q4': ('django.db.models.fields.TextField', [], {'db_column': "'transaction_type'"}),
            'q5': ('django.db.models.fields.TextField', [], {'db_column': "'site_code'"}),
            'q6': ('django.db.models.fields.TextField', [], {'db_column': "'sender_name'"}),
            'q7': ('django.db.models.fields.TextField', [], {'db_column': "'truck_id'"}),
            'q8': ('django.db.models.fields.TextField', [], {'db_column': "'food_type'"}),
            'q9': ('django.db.models.fields.IntegerField', [], {'db_column': "'weight'"})
        }
    }

    complete_apps = ['crs']
