# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.common.lang.views import LanguagesView, LanguagesAjaxView, LanguageCreateView, AccountMessagesView


urlpatterns = patterns('',
    url(r'^languages/custom_messages', LanguagesAjaxView.as_view(),name="save_questionnaire_sms_reply"),
    (r'^languages/create', LanguageCreateView.as_view()),
    url(r'^customizemessages/$', LanguagesView.as_view(), name="languages"),
    url(r'^accountmessages/$', AccountMessagesView.as_view(), name="account_messages"),

)
