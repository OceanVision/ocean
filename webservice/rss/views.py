from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from models import NewsWebsite,News,NeoUser
from django.views.generic.detail import DetailView
from django.template import loader




def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # User is logged in
            # TODO
        else:
            # User in inactive
            return render(request, 'rss/index.html', {'message': 'User is inactive'})
    else:
        # Wrong user's data
        return render(request, 'rss/index.html', {'message': 'Your username and password didn\'t match. Please try again.'})


def logout(request):
    logout(request)
    # User is logged out
    return HttpResponseRedirect(reverse('rss:index'))

def index(request):
    from models import *


    # Insert exemplary data : TODO: i01t05 integrate neo4j and django (ocean_exemplary_data.py)
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

        u.subscribed.add(n1)
        u.subscribed.add(n2)
        print "subscribed to"
        print u.subscribed.all() #Add tests
        print u._get_pk_val()
        print type(u)
        u.save()
        n1.save()
        n2.save()




    w1 = News(url="http://google.pl",slug="google_test")
    w1.save()



    if request.user.is_authenticated():
        # Do something for authenticated users.
        return render(request, 'rss/message.html', {'message': 'You are logged in'})
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'+ str(User.objects.filter(username__exact="admin"))})


def show_news(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        print request.user
        print NeoUser.objects.filter(username__exact=str(request.user))[0]._get_pk_val()

        print NeoUser.objects.filter(username__exact=str(request.user))[0].subscribed.all()
        u = NeoUser.objects.filter(username__exact=str(request.user))[0]
        print type(NeoUser.objects.filter(username__exact=str(request.user))[0])
        print u.subscribed.all() #Add tests
        #select_related('produces')
        return render(request, 'rss/show_news.html')
    else:
        # Redirect anonymous users to login page.
       return render(request, 'rss/message.html', {'message': 'You are not logged in'})

