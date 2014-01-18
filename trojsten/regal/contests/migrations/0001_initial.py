# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Competition'
        db.create_table(u'contests_competition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('informatics', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('math', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('physics', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'contests', ['Competition'])

        # Adding model 'Series'
        db.create_table(u'contests_series', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contests.Competition'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'contests', ['Series'])

        # Adding model 'Round'
        db.create_table(u'contests_round', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contests.Series'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'contests', ['Round'])


    def backwards(self, orm):
        # Deleting model 'Competition'
        db.delete_table(u'contests_competition')

        # Deleting model 'Series'
        db.delete_table(u'contests_series')

        # Deleting model 'Round'
        db.delete_table(u'contests_round')


    models = {
        u'contests.competition': {
            'Meta': {'object_name': 'Competition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'informatics': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'math': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'physics': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'contests.round': {
            'Meta': {'object_name': 'Round'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contests.Series']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'contests.series': {
            'Meta': {'object_name': 'Series'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contests.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['contests']