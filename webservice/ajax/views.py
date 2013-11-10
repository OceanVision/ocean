from django.shortcuts import render
from rss import views as rss_views


def sign_in(request):
    return render(request, 'ajax/sign_in.html')


def edit_profile(request):
    return render(request, 'ajax/edit_profile.html')


def rss(request):
    data = rss_views.get_rss_content(request)
    if len(data) > 0:
        return re
        nder(request, 'ajax/rss_index.html', data)
    else:
        return sign_in(request)