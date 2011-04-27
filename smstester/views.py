# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.smstester.forms import SMSTesterForm
from mangrove.transport.smsplayer import smsplayer
from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import MangroveException

def index(request):
    message=""
    if request.method == 'POST':
        form = SMSTesterForm(request.POST)
        if form.is_valid():
            _message = form.cleaned_data["message"]
            _from = form.cleaned_data["from_number"]
            _to = form.cleaned_data["to_number"]
            try:
                submission_id = smsplayer.sumbit(dbm=get_db_manager(), text=_message, from_number=_from, to_number=_to)
                message=submission_id
            except MangroveException as exception:
                message=exception.message
    else:
        form = SMSTesterForm()

    return render_to_response('smstester/index.html', {'form': form,'message':message},context_instance=RequestContext(request))