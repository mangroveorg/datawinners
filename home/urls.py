# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView
from datawinners.home.views import index

urlpatterns = patterns('',
        (r'^home/$', index),
        (r'^what-is-datawinners/$', TemplateView.as_view(template_name='home/what_is_datawinners.html')),
        (r'^what-is-datawinners/definition/$', TemplateView.as_view(template_name='home/datawinners_definition.html')),
        (r'^what-is-datawinners/how-it-works/$', TemplateView.as_view(template_name='home/datawinners_how_it_works.html')),
        (r'^what-is-datawinners/features/$', TemplateView.as_view(template_name='home/datawinners_features.html')),
        (r'^what-is-datawinners/benefits/$', TemplateView.as_view(template_name='home/datawinners_benefits.html')),
        (r'^examples/$', TemplateView.as_view(template_name='home/examples.html')),
        (r'^examples/understand-who-benefits-from-services/$', TemplateView.as_view(template_name='home/example1.html')),
        (r'^examples/track-teacher-attendance/$', TemplateView.as_view(template_name='home/example2.html')),
        (r'^examples/send-services-and-aid-where-they-re-needed/$', TemplateView.as_view(template_name='home/example3.html')),
        (r'^plans-and-pricing/$', TemplateView.as_view(template_name='home/plans_and_pricing.html')),
        (r'^plans-and-pricing/plans-and-pricing/$', TemplateView.as_view(template_name='home/plans_pricing.html')),
        (r'^plans-and-pricing/consulting/$', TemplateView.as_view(template_name='home/plans_consulting.html')),
        (r'^plans-and-pricing/where-is-datawinners-available/$', TemplateView.as_view(template_name='home/plans_where_dw_available.html')),
        (r'^support-and-community/$', TemplateView.as_view(template_name='home/support_and_community.html')),
        (r'^support-and-community/support-center/$', TemplateView.as_view(template_name='home/support_center.html')),
        (r'^about-us/$', TemplateView.as_view(template_name='home/about_us.html')),
        (r'^about-us/hni/$', TemplateView.as_view(template_name='home/hni.html')),
        (r'^about-us/news-events-blog-social-media/$', TemplateView.as_view(template_name='home/news.html')),
        (r'^about-us/partners/$', TemplateView.as_view(template_name='home/partners.html')),
        (r'^about-us/contact-us/$', TemplateView.as_view(template_name='home/contact_us.html')),
        (r'^privacy/$', TemplateView.as_view(template_name='home/privacy.html')),
        (r'^terms-and-conditions/$', TemplateView.as_view(template_name='home/terms_and_conditions.html')),
    )
