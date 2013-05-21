from django.conf.urls.defaults import patterns
from datawinners.feeds.views import feed_entries

urlpatterns = patterns('', (r'^feeds/(?P<form_code>\w+?)/$', feed_entries))
