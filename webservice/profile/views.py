from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import django.contrib.auth

from rss.models import NeoUser, NewsWebsite, News, UserProfile

def index(request):
    # Logged in
    if request.user.is_authenticated():
        given_username = request.GET['n'].encode('utf8').split("?ajax=ok")[0]
        user = User.objects.filter(username__exact=given_username)
        neouser = NeoUser.objects.filter(username__exact=given_username)
        if not user:
            return render(request, 'profile/index.html', {'message': 'User does not exist.'})
        user = user[0]

        user_profile = UserProfile.objects.filter(user=user.pk)
        # Initialize user profile if not present
        if len(user_profile) == 0:
            UserProfile.objects.create(
                user=user,
                description='',
                profile_image=None,
                show_email=True
            )
        user_profile = user_profile[0]

        date_joined = str(user.date_joined.year) + '.' +\
            str(user.date_joined.month) + '.' +\
            str(user.date_joined.day)
        user_email = "(email hidden by user)"
        if user_profile.show_email:
            user_email = user.email
        return render(request, 'profile/index.html', {
            'message' : '',
            'username' : user.username,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'email' : user_email,
            'date_joined' : date_joined,
            'is_staff' : user.is_staff,
            'is_online' : user.is_authenticated,
            'profile_description' : user_profile.description,
            }
        )
    else:
        return HttpResponse(content="fail", content_type="text/plain")

