from django.conf.urls.defaults import patterns, url

from datawinners.blue import view
from datawinners.blue.view import ProjectUpload, ProjectUpdate, ProjectBuilder
from datawinners.blue.view import new_xform_submission_get
from datawinners.blue.view import new_xform_submission_post, edit_xform_submission_post, attachment_download, \
    external_itemset
from datawinners.project.views.submission_views import edit_xform_submission_get

urlpatterns = patterns('',
                       url(r'^xlsform/upload/$', ProjectUpload.as_view(), name="import_project"),
                       url(r'^xlsform/download/$', view.project_download),
                       url(r'^xlsform/upload/update/(?P<project_id>\w+?)/$', ProjectUpdate.as_view(),
                           name="update_project"),
                       url(r'^xlsform/itemset/(?P<questionnaire_code>.+?)$', external_itemset),

                       url(r'^xlsform/(?P<project_id>.+?)/web_submission/(?P<survey_response_id>[^\\/]+?)/$',
                           edit_xform_submission_get, name="edit_xform_submission"),
                       url(r'^xlsform/(?P<project_id>\w+?)/web_submission/$', new_xform_submission_get,
                           name="xform_web_questionnaire"),
                       url(r'^xlsform/web_submission/(?P<survey_response_id>.+?)/$', edit_xform_submission_post,
                           name="update_web_submission"),
                       url(r'^xlsform/web_submission/$', new_xform_submission_post, name="new_web_submission"),
                       url(r'^xlsform/(?P<project_id>.+?)/$',ProjectBuilder.as_view()),
                       url(r'^download/attachment/(?P<document_id>.+?)/(?P<attachment_name>[^\\/]+?)/$',
                           attachment_download)
                       )
