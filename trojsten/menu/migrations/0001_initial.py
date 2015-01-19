# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MenuItem'
        db.create_table(u'menu_menuitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=196)),
            ('glyphicon', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('active_url_pattern', self.gf('django.db.models.fields.CharField')(max_length=196, blank=True)),
        ))
        db.send_create_signal(u'menu', ['MenuItem'])

        # Adding model 'MenuGroup'
        db.create_table(u'menu_menugroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('staff_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'menu_groups', to=orm['sites.Site'])),
        ))
        db.send_create_signal(u'menu', ['MenuGroup'])

        # Adding unique constraint on 'MenuGroup', fields ['position', 'site']
        db.create_unique(u'menu_menugroup', ['position', 'site_id'])


        # Adding SortedM2M table for field items on 'MenuGroup'
        db.create_table(u'menu_menugroup_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('menugroup', models.ForeignKey(orm[u'menu.menugroup'], null=False)),
            ('menuitem', models.ForeignKey(orm[u'menu.menuitem'], null=False)),
            ('sort_value', models.IntegerField())
        ))
        db.create_unique(u'menu_menugroup_items', ['menugroup_id', 'menuitem_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'MenuGroup', fields ['position', 'site']
        db.delete_unique(u'menu_menugroup', ['position', 'site_id'])

        # Deleting model 'MenuItem'
        db.delete_table(u'menu_menuitem')

        # Deleting model 'MenuGroup'
        db.delete_table(u'menu_menugroup')

        # Removing M2M table for field items on 'MenuGroup'
        db.delete_table(db.shorten_name(u'menu_menugroup_items'))


    models = {
        u'menu.menugroup': {
            'Meta': {'unique_together': "((u'position', u'site'),)", 'object_name': 'MenuGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('sortedm2m.fields.SortedManyToManyField', [], {'related_name': "u'groups'", 'symmetrical': 'False', 'to': u"orm['menu.MenuItem']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'menu_groups'", 'to': u"orm['sites.Site']"}),
            'staff_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'menu.menuitem': {
            'Meta': {'object_name': 'MenuItem'},
            'active_url_pattern': ('django.db.models.fields.CharField', [], {'max_length': '196', 'blank': 'True'}),
            'glyphicon': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '196'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['menu']