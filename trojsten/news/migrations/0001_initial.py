# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Entry'
        db.create_table(u'news_entry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'news_entries', to=orm['people.User'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from=u'title', unique_with=())),
        ))
        db.send_create_signal(u'news', ['Entry'])

        # Adding M2M table for field sites on 'Entry'
        m2m_table_name = db.shorten_name(u'news_entry_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm[u'news.entry'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['entry_id', 'site_id'])


    def backwards(self, orm):
        # Deleting model 'Entry'
        db.delete_table(u'news_entry')

        # Removing M2M table for field sites on 'Entry'
        db.delete_table(db.shorten_name(u'news_entry_sites'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'news.entry': {
            'Meta': {'ordering': "(u'-pub_date',)", 'object_name': 'Entry'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'news_entries'", 'to': u"orm['people.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "u'title'", 'unique_with': '()'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'people.address': {
            'Meta': {'object_name': 'Address'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'})
        },
        u'people.school': {
            'Meta': {'ordering': "(u'city', u'street', u'verbose_name')", 'object_name': 'School'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'addr_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'people.user': {
            'Meta': {'object_name': 'User'},
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_index': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "u'M'", 'max_length': '2'}),
            'graduation': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'home_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'lives_here'", 'null': 'True', 'to': u"orm['people.Address']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mailing_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'accepting_mails_here'", 'null': 'True', 'to': u"orm['people.Address']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['people.School']", 'null': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['news']