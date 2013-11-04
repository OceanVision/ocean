from django.shortcuts import render


def index(request):
    return render(request, 'base/base.html', {'navigator_item_color': 'e5e5e5'})


def get_sign_in_view(request):
    return render(request, 'base/signInForm.html')


def get_edit_profile_view(request):
    return render(request, 'base/editProfileForm.html')