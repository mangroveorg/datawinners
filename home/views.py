# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response

def index(request):
    return render_to_response('home/index.html')
