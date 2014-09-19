from django.conf.urls import patterns, include, url
from django.contrib import admin
import trojsten.submit.urls
import trojsten.results.urls
import trojsten.news.urls
import trojsten.task_statements.urls

admin.autodiscover()

from wiki.urls import get_pattern as get_wiki_pattern
from django_notify.urls import get_pattern as get_notify_pattern
from trojsten.regal.people.forms import TrojstenUserCreationForm, TrojstenUserChangeForm

# Override default forms in ksp_login
urlpatterns = patterns('ksp_login.views',
    url(r'^ucet/register/$', 'register', {'creation_form': TrojstenUserCreationForm, }, name='trojsten_register'),
    url(r'^ucet/$', 'settings', {'settings_form': TrojstenUserChangeForm, }, name='trojsten_account_settings'),
)

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'trojsten.views.home', name='home'),
    # url(r'^trojsten/', include('trojsten.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/',
    # include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^odovzdavanie/', include(trojsten.submit.urls)),
    url(r'^vysledky/', include(trojsten.results.urls)),
    url(r'^novinky/', include(trojsten.news.urls)),
    url(r'^ulohy/', include(trojsten.task_statements.urls)),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', get_wiki_pattern()),
)
