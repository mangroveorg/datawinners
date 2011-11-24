# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage

class FeatureAwareTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(FeatureAwareTemplateView, self).get_context_data(**kwargs)
        return RequestContext(self.request, context)


def index(request):
    language = request.session.get("django_language", "en")
    return redirect("/%s/home/" % language)

def switch_language(request, language):
    request.session['django_language'] = language
    if request.META.has_key('HTTP_REFERER'):
        referer= '/' + '/'.join(request.META['HTTP_REFERER'].split('/')[3:])
    else:
        referer= '/'

    if referer[:4] in ["/en/", "/fr/"]:
        referer = "/%s/%s" % (language, referer[4:])

    return redirect(referer)

def ask_us(request):
    if request.method == "GET":
        return redirect(index)
    subject = request.POST.get("subject", _("Support"))
    from_email = request.POST["email"]
    body = _("From")+": "+from_email+"\n"+\
           _("Category")+": "+request.POST["category"]+"\n\n"+\
           request.POST["message"]\
           +request.POST["to"]
    to = "herihaja@hni.org"
    #to = request.POST["to"]+"@datawinners.com"
    email = EmailMessage(subject, body, from_email=from_email, to=[to])
    if request.FILES.has_key("attachement"):
        email.attach(request.FILES["attachement"].name, request.FILES["attachement"].read())
    email.send()
    return redirect(request.POST["redirect_url"])