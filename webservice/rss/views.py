from ocean_master import OC


from django.shortcuts import render
from django.contrib.auth.models import User
from models import NeoUser, NewsWebsite, News
from django.http import HttpResponse
from rss import models
from py2neo import neo4j
from py2neo import node, rel
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.template import loader
from ocean import utils
from graph_defines import *
import urllib2
import xml.dom.minidom
import py2neo
import json
import random


def get_category_array(request):
    #TODO: make color dependent of various features
    category_array = [{'name': 'Barack Obama', 'color': 'ffbd0c'},
                      {'name': 'tennis', 'color': '00c6c4'},
                      {'name': 'iPhone', 'color': '74899c'},
                      {'name': 'cooking', 'color': '976833'}]
    return category_array




@utils.error_writing
@utils.timed
def get_loved_it_list(request):
    if 'pk' not in request.GET:
        raise Exception("Not passed primary key to loved_it view")
    news = News.objects.filter(pk=int(request.GET['pk']))[0] #TODO: add some kind of caching here
    return HttpResponse(json.dumps([user.username for user in news.loved.all()]))

@utils.error_writing
@utils.timed
def loved_it(request):
    #TODO: how to handle errors in views like this?
    if 'pk' not in request.GET:
        raise Exception("Not passed primary key to loved_it view")
    news = News.objects.filter(pk=int(request.GET['pk']))[0] #TODO: add some kind of caching here
    user = NeoUser.objects.filter(username__exact=request.user.username)[0] #TODO: add some kind of caching here
    user.loves_it.add(news)
    news.loved_counter += 1

    #TODO: Issue from github
    user.save()
    news.save()

    return HttpResponse(json.dumps({}))

@utils.error_writing
@utils.timed
def unloved_it(request):

    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/") # That's fine, connection pool

    #TODO: how to handle errors in views like this?
    if 'pk' not in request.GET:
        raise Exception("Not passed primary key to loved_it view")
    news = News.objects.filter(pk=int(request.GET['pk']))[0] #TODO: add some kind of caching here
    user = NeoUser.objects.filter(username__exact=request.user.username)[0] #TODO: add some kind of caching here


    print news.loved_counter

    delete_cypher_params = {"user_pk":user.pk, "news_pk": news.pk, "rel_name": LOVES_IT_RELATION}
    print delete_cypher_params
    print user.loves_it.all()

    delete_cypher = \
        """
        START n=node( { user_pk } ) , c=node( { news_pk } )
        MATCH n-[rel:__loves_it__]->c
        DELETE rel
        RETURN count(rel);
        """

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher(delete_cypher, delete_cypher_params)
    result = my_batch.submit()

    print "Removed ",result[0], "relations"

    # We can save here as unloving is not often called
    news.loved_counter -= result[0]
    news.save()

    #Unfortunately Neo4Django relationship removal sucks
    #user.loves_it.remove(news)
    #Not saving on purpose here! it can be lazy because likes are not critical
    return HttpResponse(json.dumps({}))


import sys
# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
@utils.timed
def graph_view_all_subscribed(graph_display):
    """ @param graph_display now represented as dictionary
    """
    print "call to graph_view_all_subscribed"
    #TODO: dziala dosyc niestabilnie i w ogole nie ma lapania wyjatkow...
    try:

        rss_items_array = []  # building news to be rendered (isn't very efficient..)
        user = NeoUser.objects.filter(username__exact=graph_display["username"])[0]
        user.refresh()
        loved = [news.link for news in user.loves_it.all()]
        print loved

        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        # Get news for authenticated users.


        #TODO: Skrajnie niewydajne..
        for rss_channel in user.subscribes_to.all():
            for news in rss_channel.produces.all():
                news_dict = news.__dict__["_prop_values"]
                news_dict['pk'] = news.pk
                news_dict['loved'] = int(news.link in loved)
                news_dict['color'] = colors[random.randint(0, 4)]
                rss_items_array.append(news_dict)
                print "Processed ",news.link

        category_array = get_category_array(graph_display)


        page = 0
        page_size = 20
        if 'page' in graph_display:
            page = int(graph_display['page'])
            page_size = int(graph_display['page_size'])

        a = page * page_size
        if a < len(rss_items_array):
            b = (page + 1) * page_size
            if b <= len(rss_items_array):
                rss_items_array = rss_items_array[a:b]
            else:
                rss_items_array = rss_items_array[a:]
        else:
            rss_items_array = None

    except Exception, e:
        print "Exception in graph_view_all_subscribed : ",e
        return {}

    return {'signed_in': True,
            'rss_items': rss_items_array,
            'categories': category_array}




def get_graph(request, dict_update):
    """ @param dict_update this dict will update request.GET
    """
    #TODO: move authentication from here!
    if request.user.is_authenticated():
        temp_dict = dict(request.GET)
        temp_dict["username"] = request.user.username # each graph_display should have username..
        temp_dict.update(dict_update)


        # @note: this function will be moved to OceanMaster
        if "graph_view" in temp_dict:
            if temp_dict["graph_view"] == "Subscribed":
                return graph_view_all_subscribed(temp_dict)
            elif temp_dict["graph_view"] == "TrendingNews":
                return {'signed_in': True,
                        'rss_items': [],
                        'categories': get_category_array()}
            else:
                raise Exception("Not recognized descriptor")
        else:
            raise Exception("No graph_view in request")

    else:
        return {}


@utils.view_error_writing
def trending_news(request):
    data = get_graph(request, {"graph_view": "TredningNews"})
    if len(data) > 0:
        data["options"] = json.dumps([{"list": ["ala", "kota"], "state":0, "action":"test_action"}
            , {"list":["murzyn", "murzyni"], "state":0, "action":"test_action"}])
        data["descriptor"] = json.dumps("ListDisplay")
        return utils.render(request, 'rss/index.html', data)
    else:
        return HttpResponse(content="fail", content_type="text/plain")

@utils.view_error_writing
def index(request):
    data = get_graph(request, {"graph_view": "Subscribed"})
    if len(data) > 0:
        data["descriptor"] = json.dumps("ListDisplay")
        return utils.render(request, 'rss/index.html', data)
    else:
        return HttpResponse(content="fail", content_type="text/plain")


def get_rss_channels(request):
    """Get subscribed RSS channels list from databasa."""
    if request.user.is_authenticated():
        rss_items_array = []  # building news to be rendered (isn't very efficient..)
        user = NeoUser.objects.filter(username__exact=request.user.username)[0]

        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        # Get news for authenticated users.
        for channel in user.subscribes_to.all():
            rss_items_array += [
                {
                    'pk' : channel.pk,
                    'title': channel.title,
                    'description': channel.description,
                    'link': channel.link,
                    'category': 2,
                    'color': colors[random.randint(0, 4)]
                }
            ]


        category_array = get_category_array(request)

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
                'rss_channels': rss_items_array,
                'categories': category_array,
                'message': ''}

    else:
        return {}


#TODO: chyba nie o to chodzi w tej funkcji manage, ona powinna obslugiwac bledy czy cos?
@utils.view_error_writing
def manage(request, message=''):
    """ @param message - additional web message f.e. error."""
    data = get_rss_channels(request)
    data['message'] = message
    if len(data) > 0:
        return utils.render(request, 'rss/channels.html', data)
    else:
        return HttpResponse(content='fail', content_type='text/plain')

@utils.view_error_writing
def get_news(request):
    print "Request from list_display=",request.GET["descriptor"]
    data = get_graph(request)
    if len(data) > 0:
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(content="fail", content_type="text/plain")



@utils.view_error_writing
def add_channel(request):
    if request.user.is_authenticated():
        graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        my_batch = neo4j.WriteBatch(graph_db)
        #TODO: efficient   query plx0r
        check_data_cypher = "START n=node(*) " + \
                            "MATCH n-[rel:__subscribes_to__]-c " + \
                            "WHERE HAS(n.username) AND n.username=\"" + request.user.username + "\" AND c.link={link} " + \
                            "RETURN c; "
        #TODO: Try to solve "?ajax=ok" problem another way.
        my_batch.append_cypher(check_data_cypher, {"link": request.GET["link"].encode("utf8").split("?ajax=ok")[0]})
        list = my_batch.submit()

        if list[0] is None:
            if not NewsWebsite.objects.filter(link=request.GET["link"].split("?ajax=ok")[0]):

                def get_node_value(node, value):
                    return node.getElementsByTagName(value)[0].childNodes[0].nodeValue.strip()

                #TODO: Try to solve "?ajax=ok" problem another way.
                response = urllib2.urlopen(request.GET["link"].split("?ajax=ok")[0])
                html = response.read()
                doc = xml.dom.minidom.parseString(html)
                channel = doc.childNodes[0].getElementsByTagName("channel")[0]
                title = get_node_value(channel, "title")
                description = get_node_value(channel, "description")
                language = get_node_value(channel, "language")
                image_tag = channel.getElementsByTagName("image")
                image_width = ""
                image_height = ""
                image_link = ""
                image_url = ""
                if image_tag:
                    image_width = int(get_node_value(channel, "width"))
                    image_height = int(get_node_value(channel, "height"))
                    image_link = get_node_value(channel, "link")
                    image_url = get_node_value(channel, "url")

                channel_node = NewsWebsite.objects.create(link=request.GET["link"].split("?ajax=ok")[0],
                                                          title=title, description=description,
                                                          image_width=image_width, image_height=image_height,
                                                          image_link=image_link, image_url=image_url,
                                                          language=language, source_type="rss")
                channel_node.save()

            else:
                #TODO: Try to solve "?ajax=ok" problem another way.
                channel_node = NewsWebsite.objects.filter(link__exact=request.GET["link"])[0].split("?ajax=ok")[0]

            # Add subscription
            user = NeoUser.objects.filter(username__exact=request.user.username)[0]
            user.subscribes_to.add(channel_node)
            user.save()

            # Another way
            #graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
            #subscribe_relation = py2neo.rel(user, models.SUBSCRIBES_TO_RELATION, channel_node)
            #graph_db.create(subscribe_relation)

            return manage(request)
        else:
            return render(request, 'rss/message.html', {'message': 'Channel already exists in users subscriptions'})
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})


@utils.view_error_writing
def delete_channel(request):
    if request.user.is_authenticated():
        graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        my_batch = neo4j.WriteBatch(graph_db)
        check_data_cypher = "START n=node(*) " + \
                            "MATCH n-[rel:__subscribes_to__]-c " + \
                            "WHERE HAS(n.username) AND n.username=\"" + request.user.username + "\" AND c.link={link} " + \
                            "RETURN c; "
        #TODO: Try to solve "?ajax=ok" problem another way.
        my_batch.append_cypher(check_data_cypher, {"link": request.GET["link"].encode("utf8").split("?ajax=ok")[0]})
        list = my_batch.submit()

        if list[0] is not None:
            graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
            my_batch = neo4j.WriteBatch(graph_db)
            #TODO: it is like the worst query we can have here : look at every single relation user->newswebsite..
            delete_cypher = "START n=node(*) " + \
                            "MATCH n-[rel:__subscribes_to__]-c " + \
                            "WHERE HAS(n.username) AND n.username=\"" + request.user.username + "\" AND c.link={link} " + \
                            "DELETE rel; "
            my_batch.append_cypher(delete_cypher, {"link": request.GET["link"].encode("utf8").split("?ajax=ok")[0]})
            my_batch.submit()

            # Doesn't work because of "lazy nodes"
            # channel = user.subscribes_to.filter(link__exact=request.GET["link"])[0]
            # channel.subscribed.remove(user)
            # user.save()

            #return HttpResponse(content="Ok")
            return manage(request)
        else:
            return render(request, 'rss/message.html', {'message': "It's not users subscription."} )
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})

