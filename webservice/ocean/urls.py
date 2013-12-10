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
    url(r'^account/', include('user_account.urls', namespace="user_account")),
    url(r'^rss/', include('rss.urls', namespace="rss")),
    url(r'^sign_in$', views.sign_in),
    url(r'^edit_profile', views.edit_profile),
    url(r'^user/', include('profile.urls', namespace='profile')),
    url(r'^mission$', views.mission),
    url(r'^show_my_ocean_view$', "rss:index"),
)
