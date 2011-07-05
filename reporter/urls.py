from django.conf.urls.defaults import patterns
from datawinners.reporter.views import register, register_through_ajax

urlpatterns = patterns('',
    (r'^reporter/register$', register),
    (r'^reporter/register_via_ajax', register_through_ajax),
)
