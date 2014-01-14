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
    profile_image = forms.ImageField()

    def clean_avatar(self):
        avatar = self.cleaned_data['profile_image']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 100
            if w != max_width or h != max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')

            #validate file size
            if len(avatar) > (20 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 20k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar


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
            profile_image = form.clean_avatar()
            user_profile.description = description
            user_profile.show_email = show_email
            user_profile.profile_image = profile_image
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
        'user_account/edit_profile.html',
        { 'form' : form }
    )


def mission(request):
    return utils.render(request, 'base/mission.html')

