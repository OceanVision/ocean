from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
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
        return render(request, 'rss/index.html',
                      {'message': 'Your username and password didn\'t match. Please try again.'})


def sign_out(request):
    logout(request)
    # User is logged out
    return HttpResponseRedirect(reverse('rss:index'))


def edit_profile(request):
    # Logged in
    if request.user.is_authenticated():
        # Current password do not match
        if not request.user.check_password(request.POST['current_password']):
            return render(request, 'base/welcome.html', {'message': 'New password and retyped password do not match!'})
        new_password = request.POST['new_password']
        retyped_password = request.POST['retyped_password']
        # Two password entries match
        if new_password == retyped_password:
            User.set_password(request.user, new_password)
            request.user.save()
            return HttpResponse(content="Ok")
        else:
            return render(request, 'rss/message.html', {'message': 'New password and retyped password do not match!'})
    else:
        return render(request, 'rss/message.html', {'message': 'You are not allowed to this page!'})
