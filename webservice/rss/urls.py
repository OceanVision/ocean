from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^show_news/$', views.show_news, name='show_news'),
    url(r'^(?P<slug>[-_\w]+)/$', views.NewsView.as_view(), name='article-detail'),
)