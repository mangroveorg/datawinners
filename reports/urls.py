from django.conf.urls.defaults import patterns
from datawinners.reports.views import report,hierarchy_report

urlpatterns = patterns('',
    (r'^reports/reportperlocation', report),
    (r'^reports/reportperhierarchypath', hierarchy_report)
)