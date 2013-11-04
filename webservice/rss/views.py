from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
import django.contrib.auth
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from models import NewsWebsite,News,NeoUser
from django.views.generic.detail import DetailView
from django.template import loader



def logme(request):
    username = request.POST['username']
    password = request.POST['password']
    # TODO: add hash authentication
    user = authenticate(username=username, password=password)
    if user is not None:
        # TODO: is_active flag checking
        if user.is_active:
            django.contrib.auth.login(request, user)
            return HttpResponseRedirect("/") # TODO: not working with ajax, return here OK and do redirect in ajax
        else:
            # User in inactive
            return render(request, 'rss/index.html', {'message': 'User is inactive'})
    else:
        # Wrong user's data
        return render(request, 'rss/index.html', {'message': 'Your username and password didn\'t match. Please try again.'})


def logmeout(request):
    logout(request)
    # User is logged out
    return HttpResponseRedirect(reverse('rss:index'))

def index(request):
    #from models import *

    sub_list = NeoUser.objects.get_or_create(username=request.user)[0].subscribes_to.all()
    sub_str = ''

    for web in sub_list:
        sub_str += web.url + '; '

    if request.user.is_authenticated():
        # Do something for authenticated users.
        return render ( request, 'rss/message.html', {
            'message': 'Hello, ' + str(request.user) + '! Here are your subscriptions: ' +
            sub_str
            }
        )
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'+ str(User.objects.filter(username__exact="admin"))})

    # TODO: add as unit test

    n1 = NewsWebsite.objects.filter(url="http://antyweb.pl")
    if len(n1) == 0:
        n1 = NewsWebsite.objects.create(url="http://antyweb.pl")
        print n1._get_pk_val()
        n1.save()
        print "Inserted ",n1

    n2 = NewsWebsite.objects.filter(url="http://spidersweb.pl")
    if len(n2) == 0:
        n2 = NewsWebsite.objects.create(url="http://spidersweb.pl")
        n2.save()
        print n2._get_pk_val()
        print "Inserted ",n2

    u = NeoUser.objects.filter(username="admin")
    print "Found ",u

    if len(u) == 0:
        u = NeoUser.objects.create(username="admin")
        u.save()
        print "Inserted ",u

        u.subscribes_to.add(n1)
        u.subscribes_to.add(n2)
        print "subscribed to"
        print u.subscribes_to.all() #Add tests
        print u._get_pk_val()
        print type(u)
        u.save()
        n1.save()
        n2.save()

    #str(NeoUser.objects.filter(username__exact="admin")[0].subscribes_to.all()[]



def show_news(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        print request.user
        print NeoUser.objects.filter(username__exact="kudkudak")[0]._get_pk_val()

        print NeoUser.objects.filter(username__exact="kudkudak")[0].subscribes_to.all()
        u = NeoUser.objects.filter(username__exact="kudkudak")[0]
        print type(NeoUser.objects.filter(username__exact="kudkudak")[0])
        print u.subscribes_to.all().select_related('produces') #Add tests
        return render(request, 'rss/show_news.html', {'message': 'Logged in'})
    else:
        # Redirect anonymous users to login page.
       return render(request, 'rss/message.html', {'message': 'You are not logged in'})

