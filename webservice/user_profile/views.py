from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout
import django.contrib.auth


def get_sign_in_form(request):
    return render(request, 'base/signInForm.html')


def get_edit_profile_form(request):
    return render(request, 'base/editProfileForm.html')


def sign_in(request):
    username = request.POST['username']
    password = request.POST['password']
    # TODO: add hash authentication
    user = authenticate(username=username, password=password)
    if user is not None:
        # TODO: is_active flag checking
        if user.is_active:
            django.contrib.auth.login(request, user)
            return HttpResponse(content="Ok")
        else:
            # User in inactive
            return render(request, 'rss/index.html', {'message': 'User is inactive'})
    else:
        # Wrong user's data
        return render(request, 'rss/index.html', {'message': 'Your username and password didn\'t match. Please try again.'})


def sign_out(request):
    logout(request)
    # User is logged out
    return HttpResponseRedirect(reverse('rss:index'))