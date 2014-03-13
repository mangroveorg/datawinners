# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.template import Template
from django.template.context import Context
from django.test import TestCase


class TestQuestionnairePreviewTags(TestCase):

    fixtures = ['test_data.json']

    def test_format_organization_number_should_not_format_a_single_number(self):
        t = Template("{% load questionnaire_preview_tags %}{{ org_number|format_organization_number }}")
        c = Context({'org_number':1234})
        rendered_template = t.render(c)
        self.assertEqual('1234', rendered_template)

    def test_format_organization_number_should_format_when_org_number_is_a_list(self):
        t = Template("{% load questionnaire_preview_tags %}{{ org_number|format_organization_number }}")
        c = Context({'org_number':[1234,4312]})
        rendered_template = t.render(c)
        self.assertEqual('<a class="org_number_link" href="/en/your-account-phone-number/" target="_blank">Your Trial Account Phone Number</a>', rendered_template)
