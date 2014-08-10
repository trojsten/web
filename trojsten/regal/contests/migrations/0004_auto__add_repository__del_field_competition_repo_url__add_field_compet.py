# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Repository'
        db.create_table(u'contests_repository', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('notification_string', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
        ))
        db.send_create_signal(u'contests', ['Repository'])

        # Deleting field 'Competition.repo_url'
        db.delete_column(u'contests_competition', 'repo_url')

        # Adding field 'Competition.repo'
        db.add_column(u'contests_competition', 'repo',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['contests.Repository']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Repository'
        db.delete_table(u'contests_repository')


        # User chose to not deal with backwards NULL issues for 'Competition.repo_url'
        raise RuntimeError("Cannot reverse this migration. 'Competition.repo_url' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Competition.repo_url'
        db.add_column(u'contests_competition', 'repo_url',
                      self.gf('django.db.models.fields.CharField')(max_length=128),
                      keep_default=False)

        # Deleting field 'Competition.repo'
        db.delete_column(u'contests_competition', 'repo_id')


    models = {
        u'contests.competition': {
            'Meta': {'object_name': 'Competition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contests.Repository']"}),
            'repo_root': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'})
        },
        u'contests.repository': {
            'Meta': {'object_name': 'Repository'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_string': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
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