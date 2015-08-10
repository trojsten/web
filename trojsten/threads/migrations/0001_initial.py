# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Thread'
        db.create_table(u'threads_thread', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'threads', ['Thread'])

        # Adding M2M table for field sites on 'Thread'
        m2m_table_name = db.shorten_name(u'threads_thread_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('thread', models.ForeignKey(orm[u'threads.thread'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['thread_id', 'site_id'])


    def backwards(self, orm):
        # Deleting model 'Thread'
        db.delete_table(u'threads_thread')

        # Removing M2M table for field sites on 'Thread'
        db.delete_table(db.shorten_name(u'threads_thread_sites'))


    models = {
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'threads.thread': {
            'Meta': {'object_name': 'Thread'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['threads']