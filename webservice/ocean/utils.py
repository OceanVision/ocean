from django.template import Context, Template
from django.http import HttpResponse
from django.shortcuts import render as django_render
import settings
import re
from django.http import HttpResponse

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



#TODO: add generic error handling and timing utility

def view_error_writing(func):
    """ This decorator will return response to message.html with error if catched error """
    def f(request, *args, **dict_args):
        f.__name__ = func.__name__
        try:
            return func(request, *args, **dict_args)
        except Exception, e:
            print "Failed"
            return render(request, 'rss/message.html', {'message': 'Failed {0} with {1}..'.format(
                func.__name__, e
            )})

    return f

def error_writing(func):
    """ This decorator will return response to message.html with error if catched error """
    def f(request, *args, **dict_args):
        try:
            return func(request, *args, **dict_args)
        except Exception, e:
            print 'Failed {0} with {1}..'.format(
                func.__name__, e)


    return f

import time
def timed(func):
    """ Decorator for easy time measurement """
    def timed(request, *args, **dict_args):
        timed.__name__ = func.__name__
        tstart = time.time()
        result = func(request, *args, **dict_args)
        tend = time.time()
        print "{0} ({1}, {2}) took {3:2.4f} s to execute".format(func.__name__, len(args), len(dict_args), tend - tstart)
        return result

    return timed