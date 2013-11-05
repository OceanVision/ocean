from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^get_sign_in_form$', views.get_sign_in_form),
    url(r'^get_edit_profile_form$', views.get_edit_profile_form),
    url(r'^sign_in$', views.sign_in, name='sign_in'),
    url(r'^sign_out$', views.sign_out, name='sign_out'),
    url(r'^edit_profile$', views.edit_profile, name='edit_profile'),
)
