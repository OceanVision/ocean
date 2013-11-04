from django.shortcuts import render


def index(request):
    return render(request, 'base/base.html', {'navigator_item_color': 'e5e5e5', 'logged_in': False})

def sign_in(request):
    return render(request, 'base/signInForm.html')

def edit_profile(request):
    return render(request, 'base/editProfileForm.html')

