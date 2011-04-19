from django.conf.urls.defaults import patterns
from datawinners.reports.views import report,hierarchy_report

urlpatterns = patterns('',
    (r'^reports/location', report),
    (r'^reports/hierarchy', hierarchy_report)
)