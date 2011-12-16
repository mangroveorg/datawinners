# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.alldata.views import index
from datawinners.alldata.views import failed_submissions

urlpatterns = patterns('',
    (r'^alldata/$', index),
    (r'^allfailedsubmissions$', failed_submissions),
)
