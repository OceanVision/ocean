from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ocean.views.home', name='home'),
    # url(r'^ocean/', include('ocean.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', views.index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_profile/', include('user_profile.urls', namespace="user_profile")),
    url(r'^rss/', include('rss.urls', namespace="rss")),
    url(r'^sign_in$', views.sign_in),
    url(r'^edit_profile', views.edit_profile),
    url(r'^mission$', views.mission),
    url(r'^show_my_ocean_view$', "rss:index"),
)
