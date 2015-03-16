# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.home.views import index, switch_language, ask_us, blog, custom_home, open_skype

urlpatterns = patterns('',
        # (r'^home/$', index),
        (r'^switch/(?P<language>.{2}?)/$', switch_language),
        # (r'^home/ask-us/', ask_us),
        # (r'^fr/about-us/blog/$', blog, {'language': 'fr'}),
        # (r'^en/about-us/blog/$', blog, {'language': 'en'}),
        # url(r'^$', custom_home),
        url(r'^openskype/', open_skype, name='open_skype'),
)