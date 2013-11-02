from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from models import NewsWebsite,News
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

    n = NewsWebsite(url="http://google.pl")
    n.save()

    w1 = News(url="http://google.pl",slug="google_test")
    w1.save()

    print NewsWebsite.objects.all()


    if request.user.is_authenticated():
        # Do something for authenticated users.
        return render(request, 'rss/message.html', {'message': 'You are logged in'})
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'+ str(User.objects.filter(username__exact="admin"))})


def show_news(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.

        
        return render(request, 'rss/show_news.html')
    else:
        # Redirect anonymous users to login page.
       return render(request, 'rss/message.html', {'message': 'You are not logged in'})


class NewsView(DetailView):
    model = News
    template_name="polls/news.htm"
