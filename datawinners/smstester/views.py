# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import uuid
from atom.http_core import HttpRequest
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from datawinners.smstester.forms import SMSTesterForm
from datawinners.smstester.models import OutgoingMessage
from mangrove.errors.MangroveException import MangroveException
from datawinners.submission.views import sms
from django.http import HttpResponse

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
                if settings.USE_NEW_VUMI:
                    submission_request.POST = {"content": _message, "from_addr": _from, "to_addr": _to, "message_id":uuid.uuid1().hex}
                else:
                    submission_request.POST = {"message": _message, "from_msisdn": _from, "to_msisdn": _to, "message_id":uuid.uuid1().hex}

                response = sms(submission_request)
                message = response.content

            except MangroveException as exception:
                message = exception.message
    else:
        form = SMSTesterForm()

    return render_to_response('smstester/index.html',
            {'form': form, 'message': message}, context_instance=RequestContext(request))

@csrf_exempt
def vumi_stub(request):
    message = OutgoingMessage(from_msisdn=request.POST['from_msisdn'], to_msisdn=request.POST['to_msisdn'],
                              message=request.POST['message'])

    if "failed" in request.POST['message']:
        HttpResponse(status=400)

    message.save()

    return HttpResponse(status=201, content=json.dumps([{'id': message.id}]), content_type='application/json')