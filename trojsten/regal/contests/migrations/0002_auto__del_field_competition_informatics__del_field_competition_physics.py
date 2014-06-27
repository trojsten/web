# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Competition.informatics'
        db.delete_column(u'contests_competition', 'informatics')

        # Deleting field 'Competition.physics'
        db.delete_column(u'contests_competition', 'physics')

        # Deleting field 'Competition.math'
        db.delete_column(u'contests_competition', 'math')

        # Adding M2M table for field sites on 'Competition'
        m2m_table_name = db.shorten_name(u'contests_competition_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('competition', models.ForeignKey(orm[u'contests.competition'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['competition_id', 'site_id'])

        # Deleting field 'Series.start_date'
        db.delete_column(u'contests_series', 'start_date')

        # Adding field 'Series.number'
        db.add_column(u'contests_series', 'number',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Competition.informatics'
        db.add_column(u'contests_competition', 'informatics',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Competition.physics'
        db.add_column(u'contests_competition', 'physics',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Competition.math'
        db.add_column(u'contests_competition', 'math',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Removing M2M table for field sites on 'Competition'
        db.delete_table(db.shorten_name(u'contests_competition_sites'))

        # Adding field 'Series.start_date'
        db.add_column(u'contests_series', 'start_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 6, 26, 0, 0)),
                      keep_default=False)

        # Deleting field 'Series.number'
        db.delete_column(u'contests_series', 'number')


    models = {
        u'contests.competition': {
            'Meta': {'object_name': 'Competition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'})
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
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['contests']