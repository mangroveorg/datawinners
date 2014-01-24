# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage
from django.conf import settings
import feedparser
from BeautifulSoup import BeautifulSoup
import time

# class FeatureAwareTemplateView(TemplateView):
#     def get_context_data(self, **kwargs):
#         context = super(FeatureAwareTemplateView, self).get_context_data(**kwargs)
#         return RequestContext(self.request, context)

def custom_home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        return index(request)

def index(request):
    language = request.session.get("django_language", "en")
    return redirect("/%s/home/" % language)

def switch_language(request, language):
    request.session['django_language'] = language
    if request.META.has_key('HTTP_REFERER'):
        referrer= '/' + '/'.join(request.META['HTTP_REFERER'].split('/')[3:])
    else:
        referrer= '/'

    if referrer[:4] in ["/en/", "/fr/"]:
        referrer = "/%s/%s" % (language, referrer[4:])

    return redirect(referrer)

def ask_us(request):
    if request.method == "GET":
        return redirect(index)

    subject = request.POST.get("subject", _("Support"))
    from_email = request.POST["email"]

    body = _("From")+": "+from_email+"\n"+\
           _("Category")+": "+request.POST["category"]+"\n\n"+\
           request.POST["message"]

    to = request.POST["to"]+"@datawinners.com"
    email = EmailMessage(subject, body, from_email=from_email, to=[to])

    if request.FILES.has_key("attachement"):
        email.attach(request.FILES["attachement"].name, request.FILES["attachement"].read())

    email.send()
    return redirect(request.POST["redirect_url"])


def _remove_social_links(content):
    soup = BeautifulSoup(content)
    social_links = soup.findAll('a', {'rel': 'nofollow'})
    [link.extract() for link in social_links]
    return soup.renderContents()


def blog(request, language):
    rss = feedparser.parse(settings.HNI_BLOG_FEED)
    posts = []
    for feed in rss.entries:
        content = _remove_social_links(feed.content[0].value)
        created_month = time.strftime("%b", feed.updated_parsed)
        created_day = feed.updated_parsed.tm_mday
        row = dict(
            link = feed.link,
            title = feed.title,
            content = content,
            created_month = created_month,
            created_day = created_day,
        )
        posts.append(row)

    request.session['django_language'] = language
    template = "home/about_blog_%s.html" % (language,)
    return render_to_response(template, {"posts": posts, "rss": rss}, context_instance=RequestContext(request))

def open_skype(request):
    return HttpResponseRedirect('skype:datawinners?chat')