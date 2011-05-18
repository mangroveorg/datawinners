# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.admin.forms import EntityTypeForm
from datawinners.main.utils import get_database_manager
from mangrove.datastore.entity import define_type, get_all_entity_types
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined
from datawinners.submission.views import submit


@login_required(login_url='/login')
def create_entity(request):
    message = ""
    if request.method == 'GET':
        return render_to_response("admin/entity_management.html", {"form": EntityTypeForm()}, context_instance=RequestContext(request))
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type"].split(",")
        try:
            manager = get_database_manager(request)
            define_type(manager, entity_name)
        except EntityTypeAlreadyDefined as type_already_defined:
            message = type_already_defined.message
        else:
            message = "Entity definition successful"
    return render_to_response("admin/entity_management.html", {"form": form, 'message': message}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def register_entity(request):
    entity_types = get_all_entity_types(get_database_manager(request))
    return render_to_response("admin/register_entity.html", {"post_url" : reverse(submit), "entity_types": entity_types}, context_instance=RequestContext(request))
