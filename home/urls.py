# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView
from datawinners.home.views import index, switch_language

urlpatterns = patterns('',
        (r'^home/$', index),
        (r'^switch/(?P<language>.{2}?)/$', switch_language),
        (r'^what-is-datawinners/$', TemplateView.as_view(template_name='home/what-is-datawinners.html')),
        (r'^what-is-datawinners/features/$', TemplateView.as_view(template_name='home/datawinners_features.html')),
        (r'^what-is-datawinners/how-it-works/$', TemplateView.as_view(template_name='home/datawinners_how_it_works.html')),
        (r'^what-is-datawinners/benefits/$', TemplateView.as_view(template_name='home/datawinners_benefits.html')),
        (r'^success-story/bngrc/$', TemplateView.as_view(template_name='home/success_story_bngrc.html')),
        (r'^success-story/msi/$', TemplateView.as_view(template_name='home/success_story_msi.html')),
        (r'^success-story/santenet2/$', TemplateView.as_view(template_name='home/success_story_santenet2.html')),
        (r'^pricing/$', index),
        (r'^support/$', index),
        (r'^about-us/$', index),
    )
