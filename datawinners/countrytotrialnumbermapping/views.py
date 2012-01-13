# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def trial_account_phone_numbers(request, language):
    template = 'countrytotrialaccountmapping/trial_account_phone_number_%s.html' % (language, )
    return render_to_response(template, context_instance=RequestContext(request))
