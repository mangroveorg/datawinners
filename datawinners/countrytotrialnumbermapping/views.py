# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_view_exempt
from countrytotrialnumbermapping.helper import get_countries_in_display_format
from datawinners.countrytotrialnumbermapping.models import Country, Network, Mapping
import json

@csrf_view_exempt
def trial_account_phone_numbers(request, language):
    template = 'countrytotrialaccountmapping/trial_account_phone_number_%s.html' % (language, )
    if request.method == 'GET':
        countries = Country.objects.all()
        return render_to_response(template,{'formatted_countries':get_countries_in_display_format(countries)}, context_instance=RequestContext(request))
    if request.method == 'POST':
        return HttpResponse(json.dumps({'foo':'bar'}))
