from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from models import NewsWebsite

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
    NewsWebsite.objects.create(url="http://google.pl")
    print NewsWebsite.objects.all()
    if request.user.is_authenticated():
        # Do something for authenticated users.
        return render(request, 'rss/message.html', {'message': 'You are logged in'})
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})
