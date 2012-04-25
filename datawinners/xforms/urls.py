# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.xforms.views import formList, xform, submission

urlpatterns = patterns('',
    (r'^xforms/formList$', formList),
    (r'^xforms/submission$', submission),
    (r'^xforms/(?P<questionnaire_code>.+?)$', xform),
    (r'^authorize/$', formList),
)

