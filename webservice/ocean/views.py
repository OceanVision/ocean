from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from ocean import utils
from user_account.forms import EditProfileForm
from rss.models import UserProfile


from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
    return utils.render(request, 'base/welcome.html')

@ensure_csrf_cookie
def sign_in(request):
    return utils.render(request, 'base/sign_in.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/sign_in")
    else:
        form = UserCreationForm()
    return render(
        request,
        'base/register.html',
        { 'form': form, }
    )

def edit_profile(request):
    # Read current user profile data
    user = User.objects.filter(username__exact=request.user.username)[0]
    user_profile = UserProfile.objects.filter(user=user.pk)[0]
    current_description = user_profile.description
    current_show_email = user_profile.show_email

    if request.method == 'POST':
        # This is POST
        form = EditProfileForm(request.POST)
        if form.is_valid():
            # Process valid data
            description = form.cleaned_data['description']
            show_email = form.cleaned_data['show_email']
            #profile_image = form.clean_avatar()
            user_profile.description = description
            user_profile.show_email = show_email
            #user_profile.profile_image = profile_image
            user_profile.save()
            # Show result to the user
            return HttpResponseRedirect(
                '/user/?n=' + request.user.username
            )
    else:
        # This is a common request
        # Show form to the user
        form = EditProfileForm()
        form.fields['description'].initial = current_description
        form.fields['show_email'].initial = current_show_email
    return render(
        request,
        'user_account/edit_profile.html',
        { 'form' : form }
    )


def mission(request):
    return utils.render(request, 'base/mission.html')

