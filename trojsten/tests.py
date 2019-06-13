from django.test import TestCase, override_settings


class SmokeTest(TestCase):
    fixtures = ["sites"]

    @override_settings(SITE_ID=1, ROOT_URL_CONFIG="trojsten.urls.default")
    def test_ksp(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=2, ROOT_URL_CONFIG="trojsten.urls.default")
    def test_prask(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=3, ROOT_URL_CONFIG="trojsten.urls.default")
    def test_fks(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=4, ROOT_URL_CONFIG="trojsten.urls.default")
    def test_kms(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=6, ROOT_URL_CONFIG="trojsten.urls.wiki")
    def test_wiki(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=7, ROOT_URL_CONFIG="trojsten.urls.default")
    def test_ufo(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=8, ROOT_URL_CONFIG="trojsten.urls.default")
    def test_fx(self):
        self._assert_homepage_loads()

    @override_settings(SITE_ID=10, ROOT_URL_CONFIG="trojsten.urls.login")
    def test_login(self):
        self._assert_homepage_loads()

    def _assert_homepage_loads(self):
        response = self.client.get("/", follow=True)
        self.assertEquals(response.status_code, 200)


class LoginLinksTest(TestCase):
    fixtures = ['sites']

    @override_settings(SITE_ID=10, ROOT_URL_CONFIG='trojsten.urls.login')
    def test_links_login(self):
        response = self.client.get('/', follow=True)
        self.assertNotContains(response, 'Kontakt')
        self.assertNotContains(response, 'Sponzori')

    @override_settings(SITE_ID=1, ROOT_URL_CONFIG='trojsten.urls.default')
    def test_links_other(self):
        response = self.client.get('/', follow=True)
        self.assertContains(response, 'Kontakt')
        self.assertContains(response, 'Sponzori')
