# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.alldata.views import  projects_index, index, reports
from datawinners.alldata.views import failed_submissions

urlpatterns = patterns('',
    (r'^alldata/$', index),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions$', failed_submissions),
)
