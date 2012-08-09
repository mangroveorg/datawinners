# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from alldata.views import data_export
from alldata.views import smart_phone_instruction
from alldata.views import index, reports
from alldata.views import failed_submissions


urlpatterns = patterns('',
    url(r'^alldata/$', index, name = "alldata_index"),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions$', failed_submissions),
    (r'^dataexport/$', data_export),
    url(r'^smartphoneinstruction$', smart_phone_instruction, name = "smart_phone_instruction"),
)
