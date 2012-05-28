# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.alldata.views import index, reports
from datawinners.alldata.views import failed_submissions

urlpatterns = patterns('',
    url(r'^alldata/$', index, name = "alldata_index"),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions$', failed_submissions),
)
