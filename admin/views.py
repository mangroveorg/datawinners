# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from admin.forms import EntityTypeForm
from mangrove.datastore.entity import define_type
from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined


@login_required(login_url='/login')
def create_entity(request):
    message = ""
    if request.method == 'GET':
        return render_to_response("admin/entity_management.html", {"form": EntityTypeForm()}, context_instance=RequestContext(request))
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type"].split(",")
        try:
            define_type(get_db_manager(), entity_name)
        except EntityTypeAlreadyDefined as type_already_defined:
            message = type_already_defined.message
        else:
            message = "Entity definition successful"
    return render_to_response("admin/entity_management.html", {"form": form, 'message': message}, context_instance=RequestContext(request))
