from ocean_master import OC
from django.shortcuts import render
from django.contrib.auth.models import User
from models import NeoUser, NewsWebsite, News, ContentSource
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
from odm_client import ODMClient


def get_category_array(graph_display):
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
    if 'pk' not in request.GET:
        raise Exception("Not passed primary key to loved_it view")
    news = News.objects.filter(pk=int(request.GET['pk']))[0] #TODO: add some kind of caching here
    user = NeoUser.objects.filter(username__exact=request.user.username)[0] #TODO: add some kind of caching here

    loved = [u.username for u in news.loved.all()]
    if user.username in loved: return #returns error

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

    delete_cypher_params = {"user_pk": user.pk, "news_pk": news.pk, "rel_name": LOVES_IT_RELATION}
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

    print "Removed ", result[0], "relations"

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
def graph_view_all_subscribed(graph_view_descriptor):
    """
        @param graph_view_descriptor now represented as dictionary. We have to design it more carefully
    """
    print "call to graph_view_all_subscribed"
    #TODO: dziala dosyc niestabilnie i w ogole nie ma lapania wyjatkow...
    try:
        print "username:", graph_view_descriptor["username"]

        content_items_array = []  # building news to be rendered (isn't very efficient..)
        user = NeoUser.objects.filter(username__exact=graph_view_descriptor["username"])[0]

        user.refresh()
        loved = [news.link for news in user.loves_it.all()]


        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        # Get news for authenticated users.

        odm_client = ODMClient()
        odm_client.connect()

        for content_source in odm_client.get_children(user.uuid, "subscribes_to"):

            for content in odm_client.get_children(content_source['uuid'], "__produces__"):
                content['loved'] = int(content['link'] in loved)
                content['color'] = colors[random.randint(0, 4)]
                content_items_array.append(content)

        category_array = get_category_array(graph_view_descriptor)
        odm_client.disconnect()

        page = 0
        page_size = 20
        if 'page' in graph_view_descriptor:
            page = int(graph_view_descriptor['page'])
            page_size = int(graph_view_descriptor['page_size'])

        a = page * page_size
        if a < len(content_items_array):
            b = (page + 1) * page_size
            if b <= len(content_items_array):
                content_items_array = content_items_array[a:b]
            else:
                content_items_array = content_items_array[a:]
        else:
            content_items_array = None

    except Exception, e:
        print "Exception in graph_view_all_subscribed : ", e
        return {}

    return {'signed_in': True,
            'rss_items': content_items_array,
            'categories': category_array}


#TODO: move to ocean_master
def get_graph(request, graph_view_descriptor_in={}):
    """
        This function returns graph that will be rendered by GraphDisplay

        @param graph_view_descriptor_in this dict will update request.GET and form graph_display
        @note: state variables are more important than dict_update
    """

    #TODO: move authentication from here! (to middleware , see stackoverflow)
    if request.user.is_authenticated():
        graph_view_descriptor = dict()
        graph_view_descriptor["username"] = request.user.username # each graph_display should have username..
        graph_view_descriptor.update(graph_view_descriptor_in)


        # Ultimately override all the variables

        # TODO: missing default list display
        if "state" in request.GET:
            graph_view_descriptor.update(json.loads(request.GET["state"]))
            print "LIKEABLE=", graph_view_descriptor["likeable"]
        else:
            print "WARNING: no state in request.GET"
            graph_view_descriptor.update(dict(request.GET))


        # @note: this function will be moved to OceanMaster
        if "graph_view" in graph_view_descriptor:
            if graph_view_descriptor["graph_view"] == "Subscribed":
                data = graph_view_all_subscribed(graph_view_descriptor)
                data.update(graph_view_descriptor)
                return data

            elif graph_view_descriptor["graph_view"] == "TrendingNews":
                # Construct appriopriate GraphView (c urrently not generic :( )


                # Setup options
                option_dict = {}
                for opt in graph_view_descriptor["options"]:
                    option_dict[opt["name"]] = opt["state"]

                # Get GraphView (construct if not in cache) from Ocean Master
                gv = OC.construct_graph_view((graph_view_descriptor["graph_view"], option_dict))

                # Return data used by GraphDisplay
                data = {'signed_in': True,
                        'rss_items': gv.get_graph(graph_view_descriptor),
                        'categories': get_category_array(graph_view_descriptor)}

                print "Data updated with ",graph_view_descriptor["likeable"]

                data.update(graph_view_descriptor)

                return data
            else:
                raise Exception("Not recognized graph_view")
        else:
            raise Exception("No graph_view in request")

    else:
        return {}


@utils.view_error_writing
def trending_news(request):
    # Graph View options (that will be pased to ocean_master)
    options = [
        {"name": "period",
         "list": ["Top week", "Top day", "Top hour!"],
         "state": 0,
         "action": "rewrite_display"}
    ]
    data = get_graph(request, {"graph_view": "TrendingNews", "options": options, "page": 0, "page_size": 20})
    if len(data) > 0:
        if "descriptor" not in data:
            data["options"] = json.dumps(options)
            data["descriptor"] = json.dumps("ListDisplay")
            data["graph_view"] = json.dumps("TrendingNews")
            data["title"] = "TRENDING NEWS"
            data["likeable"] = 0

        return utils.render(request, 'rss/index.html', data)
    else:
        return HttpResponse(content="fail", content_type="text/plain")


@utils.view_error_writing
def index(request):
    data = get_graph(request, {"graph_view": "Subscribed"})
    if len(data) > 0:
        # descriptor is a parametrization which is used by GraphDisplay (maybe change name to GraphDisplayName?)
        if "descriptor" not in data:
            #Parameters that are checked by ListDisplay and used to render stuff
            #We assume index is ListDisplay btw.
            #TODO: Code this
            data["descriptor"] = json.dumps("ListDisplay")
            data["graph_view"] = json.dumps("Subscribed")
            data["title"] = "SUBSCRIBED NEWS"
            data["sortable"] = 1
            data["likeable"] = 1
        return utils.render(request, 'rss/index.html', data)
    else:
        return HttpResponse(content="fail", content_type="text/plain")


def get_rss_channels(request):
    """Get subscribed RSS channels list from databasa."""
    if request.user.is_authenticated():
        content_items_array = []  # building news to be rendered (isn't very efficient..)
        user = NeoUser.objects.filter(username__exact=request.user.username)[0]

        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        # Get news for authenticated users.

        odm_client = ODMClient()
        odm_client.connect()

        for content_source in odm_client.get_children(user.uuid, "subscribes_to"):
            content_source['category'] = 2
            content_source['color'] = colors[random.randint(0, 4)]
            content_items_array += [content_source]

        odm_client.disconnect()

        category_array = get_category_array(request)

        page = 0
        page_size = 20
        if 'page' in request.GET:
            page = int(request.GET['page'])
            page_size = int(request.GET['page_size'])

        a = page * page_size
        if a < len(content_items_array):
            b = (page + 1) * page_size
            if b <= len(content_items_array):
                content_items_array = content_items_array[a:b]
            else:
                content_items_array = content_items_array[a:]
        else:
            content_items_array = None

        return {'signed_in': True,
                'rss_channels': content_items_array,
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
    data = get_graph(request)
    print "LIKEABLE RETURNED=", data["likeable"]
    if len(data) > 0:
        return utils.render(request, 'rss/list_display_renderer.html', data)
    else:
        return HttpResponse(content="fail", content_type="text/plain")


@utils.view_error_writing
def add_content_source(request):
    if request.user.is_authenticated():

        odm_client = ODMClient()
        odm_client.connect()

        user = NeoUser.objects.filter(username__exact=request.user.username)[0]

        is_subscribed = False
        #TODO: Think about caching things like that?
        for content_source in odm_client.get_children(user.uuid, 'subscribes_to'):
            if content_source['link'] == request.GET["link"].encode("utf8").split("?ajax=ok")[0]:
                is_subscribed = True

        # If user doesn't subscribe ContentSource with given link
        if not is_subscribed:
            link = request.GET["link"].encode("utf8").split("?ajax=ok")[0]
            # If ContentSource node with given link doesn't exist
            if len(odm_client.get_by_link("ContentSource", link)) == 0:
                def get_node_value(node, value):
                    searched_nodes = node.getElementsByTagName(value)
                    if searched_nodes:
                        childs = searched_nodes[0].childNodes
                        if childs:
                            return childs[0].nodeValue.strip()
                    return ""

                #TODO: Try to solve "?ajax=ok" problem another way.
                response = urllib2.urlopen(request.GET["link"].split("?ajax=ok")[0])

                html = response.read()

                doc = xml.dom.minidom.parseString(html)


                channel = doc.getElementsByTagName("rss")[0].getElementsByTagName("channel")[0]

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

                odm_client.add_node("ContentSource", {"link": request.GET["link"].split("?ajax=ok")[0], "title": title,
                                                      "description": description, "image_width": image_width,
                                                      "image_height": image_height, "image_link": image_link,
                                                      "image_url": image_url, "language": language,
                                                      "source_type": "rss"})

            # Add subscription
            link = request.GET["link"].encode("utf8").split("?ajax=ok")[0]
            content_source = odm_client.get_by_link("ContentSource", link)

            odm_client.add_rel(user.uuid, content_source["uuid"], "subscribes_to")

            odm_client.disconnect()

            return manage(request)
        else:
            return render(request, 'rss/message.html', {'message': 'Channel already exists in users subscriptions'})

    else:
        #Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})


@utils.view_error_writing
def delete_content_source(request):
    if request.user.is_authenticated():
        odm_client = ODMClient()
        odm_client.connect()

        user = NeoUser.objects.filter(username__exact=request.user.username)[0]

        is_subscribed = False
        for content_source in odm_client.get_children(user.uuid, 'subscribes_to'):
            if content_source['link'] == request.GET["link"].encode("utf8").split("?ajax=ok")[0]:
                is_subscribed = True

        if is_subscribed:
            link = request.GET["link"].encode("utf8").split("?ajax=ok")[0]
            content_source = odm_client.get_by_link("ContentSource", link)

            odm_client.delete_rel(user.uuid, content_source["uuid"])

            odm_client.disconnect()

            return manage(request)
        else:
            return render(request, 'rss/message.html', {'message': "It's not users subscription."})
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})

