from django.shortcuts import render


def index(request):
    return render(request, 'base/welcome.html', {'navigator_item_color': 'e5e5e5'})