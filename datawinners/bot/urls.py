# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url

from datawinners.bot.views import BotView

urlpatterns = patterns('',
    url(r'^bot/$', BotView.as_view(), name='bot')
    )
