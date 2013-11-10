from django.shortcuts import render


def index(request):
    return render(request, 'base/welcome.html')


def sign_in(request):
    return render(request, 'base/sign_in.html')


def edit_profile(request):
    return render(request, 'base/edit_profile.html')