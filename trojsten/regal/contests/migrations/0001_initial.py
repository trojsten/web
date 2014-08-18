# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Repository'
        db.create_table(u'contests_repository', (
            ('notification_string', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'contests', ['Repository'])

        # Adding model 'Competition'
        db.create_table(u'contests_competition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('repo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contests.Repository'], null=True)),
            ('repo_root', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'contests', ['Competition'])

        # Adding M2M table for field sites on 'Competition'
        m2m_table_name = db.shorten_name(u'contests_competition_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('competition', models.ForeignKey(orm[u'contests.competition'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['competition_id', 'site_id'])

        # Adding model 'Series'
        db.create_table(u'contests_series', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contests.Competition'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'contests', ['Series'])

        # Adding model 'Round'
        db.create_table(u'contests_round', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contests.Series'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('visible', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'contests', ['Round'])


    def backwards(self, orm):
        # Deleting model 'Repository'
        db.delete_table(u'contests_repository')

        # Deleting model 'Competition'
        db.delete_table(u'contests_competition')

        # Removing M2M table for field sites on 'Competition'
        db.delete_table(db.shorten_name(u'contests_competition_sites'))

        # Deleting model 'Series'
        db.delete_table(u'contests_series')

        # Deleting model 'Round'
        db.delete_table(u'contests_round')


    models = {
        u'contests.competition': {
            'Meta': {'object_name': 'Competition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contests.Repository']", 'null': 'True'}),
            'repo_root': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'})
        },
        u'contests.repository': {
            'Meta': {'object_name': 'Repository'},
            'notification_string': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'contests.round': {
            'Meta': {'object_name': 'Round'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contests.Series']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {})
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
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['contests']