from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
import django.contrib.auth

from rss.models import UserProfile

def sign_in(request):
    username = request.POST['username']
    password = request.POST['password']
    # TODO: add hash authentication
    user = authenticate(username=username, password=password)
    # UserProfile init
    user_profile = UserProfile.objects.filter(user=user)
    if len(user_profile) == 0:
        UserProfile.objects.create(
            user=user,
            description='',
            show_email=True,
            profile_image=None
        )

    if user is not None:
        # TODO: is_active flag checking
        if user.is_active:
            django.contrib.auth.login(request, user)
            return HttpResponse(content="ok", content_type="text/plain")
        else:
            # User is inactive
            return HttpResponse(content="inactive_user", content_type="text/plain")
    else:
        # Wrong user's data
        return HttpResponse(content="fail", content_type="text/plain")


def sign_out(request):
    logout(request)
    # User is logged out
    return HttpResponse(content="ok", content_type="text/plain")


def change_password(request):
    # Logged in
    if request.user.is_authenticated():
        # Current password do not match
        if not request.user.check_password(request.POST['current_password']):
            return HttpResponse(content="fail", content_type="text/plain")
        new_password = request.POST['new_password']
        User.set_password(request.user, new_password)
        request.user.save()
        return HttpResponse(content="ok", content_type="text/plain")
    else:
        return HttpResponse(content="fail", content_type="text/plain")
