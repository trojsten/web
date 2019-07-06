# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import TestCase, override_settings
from wiki.models.article import Article, ArticleRevision
from wiki.models.urlpath import URLPath

from trojsten.people.models import User

TEST_INDEX = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch_backend.AsciifoldingElasticSearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "TIMEOUT": 60 * 10,
        "INDEX_NAME": "test_index",
    }
}


@override_settings(SITE_ID=6, ROOT_URLCONF="trojsten.urls.wiki", HAYSTACK_CONNECTIONS=TEST_INDEX)
@unittest.skipIf(not settings.ELASTICSEARCH_TESTS, "Elasticsearch tests skipped.")
class SearchTests(TestCase):
    def setUp(self):
        try:
            self.site = Site.objects.get(pk=6)
        except Site.DoesNotExist:
            self.site = Site.objects.create(pk=6, name="Wiki", domain="wiki.trojsten.sk")

        self.non_staff_user = User.objects.create_user(
            username="jozko", first_name="Jozko", last_name="Mrkvicka", password="pass"
        )
        self.staff_user = User.objects.create_user(
            username="staff", first_name="Staff", last_name="Staff", password="pass"
        )
        self.group = Group.objects.create(name="staff")
        self.group.user_set.add(self.staff_user)
        self.staff_user.groups.add(self.group)

        root_article = Article.objects.create()
        self.root_path = URLPath.objects.create(site=self.site, article=root_article)
        ArticleRevision.objects.create(article=root_article, title="Root article")

        public_article = Article.objects.create()
        public_article.add_revision(
            ArticleRevision.objects.create(
                title="Nadpis", content="Verejný článok a jeho text", article=public_article
            )
        )
        URLPath.objects.create(
            site=self.site, article=public_article, slug="clanok", parent=self.root_path
        )

        staff_article = Article.objects.create(
            group=self.group, other_read=False, other_write=False, group_read=True
        )
        staff_article.add_revision(
            ArticleRevision.objects.create(
                title="Top secret", content="Tento článok má tajný obsah.", article=staff_article
            )
        )
        URLPath.objects.create(
            site=self.site, article=staff_article, slug="secret", parent=self.root_path
        )

        call_command("rebuild_index", interactive=False)

    def tearDown(self):
        call_command("clear_index", interactive=False, verbosity=0)

    # Find public articles containing 'text'.
    def test_basic_search(self):
        response = self.client.get("/search/", {"q": "text"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page"].object_list), 1)
        self.assertSetEqual(
            set(["Nadpis"]), set([res.title for res in response.context["page"].object_list])
        )

    def test_no_staff_search(self):
        response = self.client.get("/search/", {"q": "tajný"})
        self.assertEqual(len(response.context["page"].object_list), 0)

    def test_ignore_diacritics_search(self):
        response = self.client.get("/search/", {"q": "clanok"})
        self.assertEqual(len(response.context["page"].object_list), 1)
        self.assertSetEqual(
            set(["Nadpis"]), set([res.title for res in response.context["page"].object_list])
        )

    # Find through all articles, which user has access to.
    def test_staff_search(self):
        self.client.force_login(self.staff_user)
        response = self.client.get("/search/", {"q": "článok"})
        self.assertEqual(len(response.context["page"].object_list), 2)
        self.assertSetEqual(
            set(["Nadpis", "Top secret"]),
            set([res.title for res in response.context["page"].object_list]),
        )

    # Create a new article and find text in it.
    def test_new_article(self):
        response = self.client.get("/search/", {"q": "novy clanok"})
        self.assertEqual(len(response.context["page"].object_list), 0)
        new_article = Article.objects.create()
        new_article.add_revision(
            ArticleRevision.objects.create(
                title="Nové novinky", content="Toto je novy clanok.", article=new_article
            )
        )
        URLPath.objects.create(
            site=self.site, article=new_article, slug="new", parent=self.root_path
        )
        call_command("update_index")
        response = self.client.get("/search/", {"q": "novy clanok"})
        self.assertSetEqual(
            set(["Nové novinky"]), set([res.title for res in response.context["page"].object_list])
        )
