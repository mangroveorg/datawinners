from django.conf.urls import patterns

urlpatterns = patterns('langcodes.views',
    (r'^langs.json', 'search'),
    (r'^validate.json', 'validate'),
)