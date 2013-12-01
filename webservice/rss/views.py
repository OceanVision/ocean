from django.shortcuts import render
from django.contrib.auth.models import User
from models import NeoUser, NewsWebsite
from django.http import HttpResponse
from rss import models
from py2neo import neo4j
from py2neo import node, rel
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.template import loader
from ocean import utils, views as ocean_views
import urllib2
import xml.dom.minidom
import py2neo
import json


# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
def get_rss_content(request):
    if request.user.is_authenticated():
        rss_items_array = []  # building news to be rendered (isn't very efficient..)
        user = NeoUser.objects.filter(username__exact=request.user.username)[0]
        # Get news for authenticated users.
        for rss_channel in user.subscribes_to.all():
            for news in rss_channel.produces.all():
                rss_items_array += [{'title': news.title, 'description': news.description,
                                     'link': news.link, 'pubDate': news.pubDate,
                                     'category': 2, 'color': '999999'}]

        #TODO: make color dependent of various features
        category_array = [{'name': 'Barack Obama', 'color': 'ffbd0c'},
                          {'name': 'tennis', 'color': '00c6c4'},
                          {'name': 'iPhone', 'color': '74899c'},
                          {'name': 'cooking', 'color': '976833'}]

        page = 0
        page_size = 20
        if 'page' in request.GET:
            page = int(request.GET['page'])
            page_size = int(request.GET['page_size'])

        a = page * page_size
        if a < len(rss_items_array):
            b = (page + 1) * page_size
            if b <= len(rss_items_array):
                rss_items_array = rss_items_array[a:b]
            else:
                rss_items_array = rss_items_array[a:]
        else:
            rss_items_array = None

        return {'signed_in': True,
                'rss_items': rss_items_array,
                'categories': category_array}
    else:
        return {}


def index(request):
    data = get_rss_content(request)
    if len(data) > 0:
        return utils.render(request, 'rss/index.html', data)
    else:
        return ocean_views.sign_in(request)


def get_news(request):
    data = get_rss_content(request)
    if len(data) > 0:
        return HttpResponse(json.dumps(data))
        # utils.render(request, 'rss/index.html', data)
    else:
        return ocean_views.sign_in(request)


#TODO: Refactor NewsWebsite ----> Content Source
#TODO: Refactor News --> Content

# TODO: refactor (it is not news channel..)
# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
def add_channel(request):
    if request.user.is_authenticated():
        graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        my_batch = neo4j.WriteBatch(graph_db)
        check_data_cypher = "START n=node(*) " + \
                            "MATCH n-[rel:__subscribes_to__]-c " + \
                            "WHERE HAS(n.username) AND n.username=\"" + request.user.username + "\" AND c.link=\"" + request.GET["link"] + "\" " + \
                            "RETURN c; "
        my_batch.append_cypher(check_data_cypher)
        list = my_batch.submit()

        if list[0] is None:
            if not NewsWebsite.objects.filter(link=request.GET["link"]):
                response = urllib2.urlopen(request.GET["link"])
                html = response.read()
                doc = xml.dom.minidom.parseString(html)
                channel = doc.childNodes[0].getElementsByTagName("channel")[0]
                title = channel.getElementsByTagName("title")[0].nodeValue
                description = channel.getElementsByTagName("description")[0].nodeValue
                image_tag = channel.getElementsByTagName("image")
                image_width = ""
                image_height = ""
                image_link = ""
                image_url = ""
                if image_tag:
                    image_width = image_tag[0].getElementsByTagName("width")[0].nodeValue
                    image_height = image_tag[0].getElementsByTagName("height")[0].nodeValue
                    image_link = image_tag[0].getElementsByTagName("link")[0].nodeValue
                    image_url = image_tag[0].getElementsByTagName("url")[0].nodeValue
                language = channel.getElementsByTagName("language")[0].nodeValue

                channel_node = NewsWebsite.objects.create(label=models.NEWS_WEBSITE_LABEL, link=request.GET["link"],
                                                          title=title, description=description,
                                                          image_width=image_width, image_height=image_height,
                                                          image_link=image_link, image_url=image_url,
                                                          language=language, source_type="rss")
                channel_node.save()

            else:
                channel_node = NewsWebsite.objects.filter(link__exact=request.GET["link"])[0]

            # Add subscription
            user = NeoUser.objects.filter(username__exact=request.user.username)[0]
            user.subscribes_to.add(channel_node)
            user.save()

            # Another way
            #graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
            #subscribe_relation = py2neo.rel(user, models.SUBSCRIBES_TO_RELATION, channel_node)
            #graph_db.create(subscribe_relation)

            return HttpResponse(content="Ok " + html)
        else:
            return HttpResponse(content="Channel already exists in users subscriptions")
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})

# TODO: refactor (it is not news channel..)
# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
def delete_channel(request):
    if request.user.is_authenticated():
        graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        my_batch = neo4j.WriteBatch(graph_db)
        check_data_cypher = "START n=node(*) " + \
                            "MATCH n-[rel:__subscribes_to__]-c " + \
                            "WHERE HAS(n.username) AND n.username=\"" + request.user.username + "\" AND c.link=\"" + request.GET["link"] + "\" " + \
                            "RETURN c; "
        my_batch.append_cypher(check_data_cypher)
        list = my_batch.submit()

        if list[0] is not None:
            graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
            my_batch = neo4j.WriteBatch(graph_db)
            delete_cypher = "START n=node(*) " + \
                            "MATCH n-[rel:__subscribes_to__]-c " + \
                            "WHERE HAS(n.username) AND n.username=\"" + request.user.username + "\" AND c.link=\"" + request.GET["link"] + "\" " + \
                            "DELETE rel; "
            my_batch.append_cypher(delete_cypher)
            my_batch.submit()

            # Doesn't work because of "lazy nodes"
            # channel = user.subscribes_to.filter(link__exact=request.GET["link"])[0]
            # channel.subscribed.remove(user)
            # user.save()
            return HttpResponse(content="Ok")
        else:
            return HttpResponse(content="It's not users subscription.")
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
