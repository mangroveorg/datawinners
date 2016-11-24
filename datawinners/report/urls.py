from django.conf.urls.defaults import patterns, url


from datawinners.report.all_reports import AllReportsView, report_content, report_stylesheet, report_font_file, \
    create_report_view, delete_report_view

urlpatterns = patterns('',
                       url(r'^reports/(?P<report_id>.+?)/delete_test_view/$', delete_report_view),
                       url(r'^reports/(?P<report_id>.+?)/create_test_view/$', create_report_view),
                       url(r'^reports/(?P<report_id>.+?)/stylesheet/$', report_stylesheet),
                       url(r'^reports/(?P<report_id>.+?)/fonts/(?P<font_file_name>.+?)/$', report_font_file),
                       url(r'reports/$', AllReportsView.as_view(), name='all_reports'),
                       url(r'^reports/(?P<report_id>.+?)/$', report_content)
                       )
