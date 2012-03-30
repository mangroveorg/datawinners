# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Country'
        db.create_table('countrytotrialnumbermapping_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country_name_en', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('country_name_fr', self.gf('django.db.models.fields.TextField')()),
            ('country_code', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('countrytotrialnumbermapping', ['Country'])

        # Adding model 'Network'
        db.create_table('countrytotrialnumbermapping_network', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network_name', self.gf('django.db.models.fields.TextField')()),
            ('trial_sms_number', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('countrytotrialnumbermapping', ['Network'])

        # Adding M2M table for field country on 'Network'
        db.create_table('countrytotrialnumbermapping_network_country', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('network', models.ForeignKey(orm['countrytotrialnumbermapping.network'], null=False)),
            ('country', models.ForeignKey(orm['countrytotrialnumbermapping.country'], null=False))
        ))
        db.create_unique('countrytotrialnumbermapping_network_country', ['network_id', 'country_id'])


    def backwards(self, orm):
        
        # Deleting model 'Country'
        db.delete_table('countrytotrialnumbermapping_country')

        # Deleting model 'Network'
        db.delete_table('countrytotrialnumbermapping_network')

        # Removing M2M table for field country on 'Network'
        db.delete_table('countrytotrialnumbermapping_network_country')


    models = {
        'countrytotrialnumbermapping.country': {
            'Meta': {'object_name': 'Country'},
            'country_code': ('django.db.models.fields.TextField', [], {}),
            'country_name': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'countrytotrialnumbermapping.network': {
            'Meta': {'object_name': 'Network'},
            'country': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['countrytotrialnumbermapping.Country']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network_name': ('django.db.models.fields.TextField', [], {}),
            'trial_sms_number': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['countrytotrialnumbermapping']
