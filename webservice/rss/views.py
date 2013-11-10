from django.shortcuts import render
from django.contrib.auth.models import User
from models import NeoUser
from django.http import HttpResponse
from rss import models
from py2neo import neo4j
from py2neo import node, rel
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.template import loader
from ocean import views as ocean_views


# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
def get_rss_content(request):
    if request.user.is_authenticated():
        rss_items_array = []  # building news to be rendered (isn't very efficient..)
        #user = NeoUser.objects.filter(username__exact=NeoUser.username)[0]
        u = NeoUser.objects.filter(username__exact="kudkudak")[0]
        # Get news for authenticated users.
        for rss_channel in u.subscribes_to.all():
            for news in rss_channel.produces.all():
                rss_items_array += [{'title': news.title, 'description': news.description,
                                     'link': news.link, 'pubDate': news.pubDate,
                                     'category': 2, 'color': 'e5e5e5'}]

        #TODO: make color dependent of various features
        category_array = [{'name': 'Barack Obama', 'color': 'ffbd0c'},
                          {'name': 'tennis', 'color': '00c6c4'},
                          {'name': 'iPhone', 'color': '74899c'},
                          {'name': 'cooking', 'color': '976833'}]

        return {'signed_in': True,
                'rss_items': rss_items_array,
                'categories': category_array}
    else:
        return {}


def index(request):
    data = get_rss_content(request)
    if len(data) > 0:
        return render(request, 'rss/rss_index.html', data)
    else:
        return ocean_views.sign_in(request)



#TODO: Refactor NewsWebsite ----> Content Source
#TODO: Refactor News --> Content

# TODO: refactor (it is not news channel..)
# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
def add_channel(request):
    if request.user.is_authenticated():
        graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        channels = [
            node(label=models.NEWS_CHANNEL_LABEL, link=request.link),
        ]
        channels = graph_db.create(*channels)
        # Create instance relations
        graph_db.create(
            rel(models.types[0], models.HAS_INSTANCE_RELATION, channels[0]),
        )

        return HttpResponse(content="Ok")
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})

# TODO: refactor (it is not news channel..)
# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
def delete_channel(request):
    if request.user.is_authenticated():
        graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        user = NeoUser.objects.filter(username__exact=User.username)[0]
        website = user.subscribes_to.all().filter(link__exact=request.link)[0]
        graph_db.delete(channel)

        return HttpResponse(content="Ok")
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})


        #def index(request):
        #    #from models import *
        #
        #    sub_list = NeoUser.objects.get_or_create(username=request.user)[0].subscribes_to.all()
        #    sub_str = ''
        #
        #    for web in sub_list:
        #        sub_str += web.url + '; '
        #
        #    if request.user.is_authenticated():
        #        # Do something for authenticated users.
        #        return render ( request, 'rss/message.html', {
        #            'message': 'Hello, ' + str(request.user) + '! Here are your subscriptions: ' +
        #            sub_str
        #            }
        #        )
        #    else:
        #        # Redirect anonymous users to login page.
        #        return render(request, 'rss/message.html', {'message': 'You are not logged in'
        #                                                        + str(request.user.objects.filter(username__exact="admin"))})
        #
        #    # TODO: add as unit test
        #
        #    n1 = NewsWebsite.objects.filter(url="http://antyweb.pl")
        #    if len(n1) == 0:
        #        n1 = NewsWebsite.objects.create(url="http://antyweb.pl")
        #        print n1._get_pk_val()
        #        n1.save()
        #        print "Inserted ",n1
        #
        #    n2 = NewsWebsite.objects.filter(url="http://spidersweb.pl")
        #    if len(n2) == 0:
        #        n2 = NewsWebsite.objects.create(url="http://spidersweb.pl")
        #        n2.save()
        #        print n2._get_pk_val()
        #        print "Inserted ",n2
        #
        #    u = NeoUser.objects.filter(username="admin")
        #    print "Found ",u
        #
        #    if len(u) == 0:
        #        u = NeoUser.objects.create(username="admin")
        #        u.save()
        #        print "Inserted ",u
        #
        #        u.subscribes_to.add(n1)
        #        u.subscribes_to.add(n2)
        #        print "subscribed to"
        #        print u.subscribes_to.all() #Add tests
        #        print u._get_pk_val()
        #        print type(u)
        #        u.save()
        #        n1.save()
        #        n2.save()
        #
        #    #str(NeoUser.objects.filter(username__exact="admin")[0].subscribes_to.all()[]