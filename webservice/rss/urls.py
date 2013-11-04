from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.logme, name='login'),
    url(r'^logout/$', views.logmeout, name='logout'),
    url(r'^show_news/$', views.show_news, name='show_news'),
)