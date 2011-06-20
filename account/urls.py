from django.conf.urls.defaults import *

urlpatterns = patterns('account.views',
                       (r'^account/$','settings'),
                       )
