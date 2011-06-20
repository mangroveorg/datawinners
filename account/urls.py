from django.conf.urls.defaults import *
from views import settings

urlpatterns = patterns('',
                       (r'^account/$',settings),
                       )
