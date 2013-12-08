from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^manage$', views.manage, name='manage'),
    url(r'^add_channel$', views.add_channel, name='add_channel'),
    url(r'^delete_channel$', views.delete_channel, name='delete_channel'),
    url(r'^get_news$', views.get_news, name='get_news'),
    url(r'^get_loved_it_list', views.get_loved_it_list, name='get_loved_it_list'),
    url(r'^loved_it', views.loved_it, name='loved_it'),
    url(r'^unloved_it', views.unloved_it, name='unloved_it')
)
