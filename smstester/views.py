# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from atom.http_core import HttpRequest
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.smstester.forms import SMSTesterForm
from mangrove.errors.MangroveException import MangroveException
from datawinners.submission.views import sms


def index(request):
    message = ""
    if request.method == 'POST':
        form = SMSTesterForm(request.POST)
        if form.is_valid():
            _message = form.cleaned_data["message"]
            _from = form.cleaned_data["from_number"]
            _to = form.cleaned_data["to_number"]
            try:
                submission_request = HttpRequest(uri=reverse(sms), method='POST')
                submission_request.POST = {"message": _message, "from_msisdn": _from, "to_msisdn": _to}

                response = sms(submission_request)
                message = response.content

            except MangroveException as exception:
                message = exception.message
    else:
        form = SMSTesterForm()

    return render_to_response('smstester/index.html',
                              {'form': form, 'message': message}, context_instance=RequestContext(request))
