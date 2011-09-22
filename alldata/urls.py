# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.alldata.views import index, datasender_dashboard
from datawinners.alldata.views import failed_submissions

urlpatterns = patterns('',
    (r'^alldata/(?P<reporter_id>.+?)/$', index),
    (r'^allfailedsubmissions$', failed_submissions),
    (r'^datasenderdasboard/$', datasender_dashboard),
)
