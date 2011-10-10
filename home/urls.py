# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView
from datawinners.home.views import index

urlpatterns = patterns('',
        (r'^home/$', index),
        (r'^home/en/$', TemplateView.as_view(template_name='home/index_en.html')),
        (r'^home/fr/$', TemplateView.as_view(template_name='home/index_fr.html')),

        (r'^en/what-is-datawinners/$', TemplateView.as_view(template_name='home/what-is-datawinners_en.html')),
        (r'^en/what-is-datawinners/features/$', TemplateView.as_view(template_name='home/datawinners_features_en.html')),
        (r'^en/what-is-datawinners/how-it-works/$', TemplateView.as_view(template_name='home/datawinners_how_it_works_en.html')),
        (r'^en/what-is-datawinners/benefits/$', TemplateView.as_view(template_name='home/datawinners_benefits_en.html')),
        (r'^fr/what-is-datawinners/$', TemplateView.as_view(template_name='home/what-is-datawinners_fr.html')),
        (r'^fr/what-is-datawinners/features/$', TemplateView.as_view(template_name='home/datawinners_features_fr.html')),
        (r'^fr/what-is-datawinners/how-it-works/$', TemplateView.as_view(template_name='home/datawinners_how_it_works_fr.html')),
        (r'^fr/what-is-datawinners/benefits/$', TemplateView.as_view(template_name='home/datawinners_benefits_fr.html')),

        (r'^en/success-stories/$', TemplateView.as_view(template_name='home/success_stories_en.html')),
        (r'^en/success-story/bngrc/$', TemplateView.as_view(template_name='home/success_story_bngrc_en.html')),
        (r'^en/success-story/msi/$', TemplateView.as_view(template_name='home/success_story_msi_en.html')),
        (r'^en/success-story/santenet2/$', TemplateView.as_view(template_name='home/success_story_santenet2_en.html')),
        (r'^fr/success-stories/$', TemplateView.as_view(template_name='home/success_stories_fr.html')),
        (r'^fr/success-story/bngrc/$', TemplateView.as_view(template_name='home/success_story_bngrc_fr.html')),
        (r'^fr/success-story/msi/$', TemplateView.as_view(template_name='home/success_story_msi_fr.html')),
        (r'^fr/success-story/santenet2/$', TemplateView.as_view(template_name='home/success_story_santenet2_fr.html')),

        (r'^en/pricing/$', TemplateView.as_view(template_name='home/pricing_en.html')),
        (r'^fr/pricing/$', TemplateView.as_view(template_name='home/pricing_fr.html')),

        (r'^en/support/$', TemplateView.as_view(template_name='home/support_en.html')),
        (r'^fr/support/$', TemplateView.as_view(template_name='home/support_fr.html')),

        (r'^en/about-us/$', TemplateView.as_view(template_name='home/about_us_en.html')),
        (r'^en/about-us/blog/$', TemplateView.as_view(template_name='home/about_blog_en.html')),
        (r'^en/about-us/partners/$', TemplateView.as_view(template_name='home/about_partners_en.html')),
        (r'^en/about-us/clients/$', TemplateView.as_view(template_name='home/about_clients_en.html')),
        (r'^en/about-us/contact-us/$', TemplateView.as_view(template_name='home/about_contact_en.html')),
        (r'^fr/about-us/$', TemplateView.as_view(template_name='home/about_us_fr.html')),
        (r'^fr/about-us/blog/$', TemplateView.as_view(template_name='home/about_blog_fr.html')),
        (r'^fr/about-us/partners/$', TemplateView.as_view(template_name='home/about_partners_fr.html')),
        (r'^fr/about-us/clients/$', TemplateView.as_view(template_name='home/about_clients_fr.html')),
        (r'^fr/about-us/contact-us/$', TemplateView.as_view(template_name='home/about_contact_fr.html')),
    )
