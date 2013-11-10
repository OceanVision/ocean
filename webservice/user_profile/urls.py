from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^sign_in$', views.sign_in, name='sign_in'),
    url(r'^sign_out$', views.sign_out, name='sign_out'),
    url(r'^edit_profile$', views.edit_profile, name='edit_profile'),
)
