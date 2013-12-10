from ocean import utils
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from rss.models import UserProfile

def index(request):
    return utils.render(request, 'base/welcome.html')


def sign_in(request):
    return utils.render(request, 'base/sign_in.html')

class ProfileEditForm(forms.Form):
    description = forms.CharField(max_length=200)
    show_email = forms.BooleanField(required=False)

def edit_profile(request):
    # Read current user profile data
    user = User.objects.filter(username__exact=request.user.username)[0]
    user_profile = UserProfile.objects.filter(user=user.pk)[0]
    current_description = user_profile.description
    current_show_email = user_profile.show_email

    if request.method == 'POST':
        # This is POST
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            # Process valid data
            description = form.cleaned_data['description']
            show_email = form.cleaned_data['show_email']
            user_profile.description = description
            user_profile.show_email = show_email
            user_profile.save()
            # Show result to the user
            return HttpResponseRedirect(
                '/user/?n=' + request.user.username
            )
    else:
        # This is a common request
        # Show form to the user
        form = ProfileEditForm()
        form.fields['description'].initial = current_description
        form.fields['show_email'].initial = current_show_email
    return render(
        request,
        'base/edit_profile.html',
        { 'form' : form }
    )


def mission(request):
    return utils.render(request, 'base/mission.html')

