from django.template import Context, Template
from django.http import HttpResponse
from django.shortcuts import render as django_render
import settings
import re


def get_raw_template(path, context={}):
    lines = open(settings.PROJECT_PATH + 'templates/' + path, 'r').readlines()
    html = ''
    for line in lines:
        html += re.sub(r'{% extends.*%}', '', line)
    return Template(html).render(Context(context))


def render(request, path, context={}):
    if 'ajax' in request.GET:
        return HttpResponse(get_raw_template(path, context))
    else:
        return django_render(request, path, context)
