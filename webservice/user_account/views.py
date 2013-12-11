from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django import forms
import django.contrib.auth
import random

from rss.models import UserProfile, PrivateMessages


def get_messages(request):
    if request.user.is_authenticated():
        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        messages_array = []
        user = User.objects.filter(username__exact=request.user.username)[0]
        contact = User.objects.filter(username__exact=request.GET['user'].split("?ajax=ok")[0])[0]

        # Get all incoming messages
        private_messages = PrivateMessages.objects.filter(
            receiver__exact=user.pk,
            sender__exact=contact.pk
        )
        for pm in private_messages:
            messages_array += [
                {
                    'author' : contact.username,
                    'date' : pm.date,
                    'private_message' : pm.message,
                    'color': colors[random.randint(0, 4)]
                }
            ]

        # Get all outgoing messages
        private_messages = PrivateMessages.objects.filter(
            receiver__exact=contact.pk,
            sender__exact=user.pk
        )
        for pm in private_messages:
            messages_array += [
                {
                    'author' : user.username,
                    'date' : pm.date,
                    'private_message' : pm.message,
                    'color': colors[random.randint(0, 4)]
                }
            ]

        # !!! !!! SORTOWANIE PO DACIE !!! !!!
        messages_array.sort(key=lambda item:item['date'], reverse=True)

        page = 0
        page_size = 20
        if 'page' in request.GET:
            page = int(request.GET['page'])
            page_size = int(request.GET['page_size'])

        a = page * page_size
        if a < len(messages_array):
            b = (page + 1) * page_size
            if b <= len(messages_array):
                messages_array = messages_array[a:b]
            else:
                messages_array = messages_array[a:]
        else:
            messages_array = None

        return {'signed_in': True,
                'messages': messages_array,
                'contact' : contact,
                'message': ''}

    else:
        return {}


class PrivateMessageForm(forms.Form):
    text = forms.CharField(max_length=2000)


def inbox(request):
    """ @param message - additional web message f.e. error."""
    # Get messages from database
    user = User.objects.filter(username__exact=request.user.username)[0]
    contact = User.objects.filter(username__exact=request.GET['user'].split("?ajax=ok")[0])[0]

    if request.method == 'POST':
        # This is POST
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            # Process valid data
            text = form.cleaned_data['text']
            pm = PrivateMessages.objects.create(
                sender=user,
                receiver=contact,
                message=text
            )
            pm.save()
            form = PrivateMessageForm()
    else:
        # This is a common request - show form to the user
        form = PrivateMessageForm()

    data = get_messages(request)
    data['form'] = form

    if len(data) > 0:
        return render(request, 'user_account/inbox.html', data)
    else:
        return HttpResponse(content='fail', content_type='text/plain')


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
