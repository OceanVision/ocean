from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add_channel$', views.add_channel, name='add_channel'),
    url(r'^delete_channel$', views.delete_channel, name='delete_channel'),
    url(r'^get_rss_content$', views.get_rss_content, name='get_rss_content'),
)