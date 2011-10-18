# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response, redirect


def index(request):
    return render_to_response('home/index_en.html')

def switch_language(request, language):
    request.session['django_language'] = language
    if request.META.has_key('HTTP_REFERER'):
        referer= '/' + '/'.join(request.META['HTTP_REFERER'].split('/')[3:])
    else:
        referer= '/'
    return redirect(referer)
