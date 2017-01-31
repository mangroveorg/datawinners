from django.conf.urls.defaults import patterns, url

from datawinners.report.admin import delete_report_view, create_report_view
from datawinners.report.views import AllReportsView, report_content, report_stylesheet, report_font_file, \
    report_image_file

urlpatterns = patterns('',
                       url(r'^reports/(?P<report_id>.+?)/delete_test_view/$', delete_report_view),
                       url(r'^reports/(?P<report_id>.+?)/create_test_view/$', create_report_view),
                       url(r'^reports/(?P<report_id>.+?)/stylesheet/$', report_stylesheet),
                       url(r'^reports/(?P<report_id>.+?)/fonts/(?P<font_file_name>.+?)/$', report_font_file),
                       url(r'^reports/(?P<report_id>.+?)/images/(?P<image_file_name>.+?)/$', report_image_file),
                       url(r'reports/$', AllReportsView.as_view(), name='all_reports'),
                       url(r'^reports/(?P<report_id>.+?)/$', report_content)
                       )
