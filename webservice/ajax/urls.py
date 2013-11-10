from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^sign_in$', views.sign_in),
    url(r'^edit_profile$', views.edit_profile),
    url(r'^rss$', views.rss),
)
