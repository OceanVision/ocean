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
    if 'uuid' not in request.GET:
        raise Exception("Not passed UUID to loved_it view")
    odm_client = ODMClient()
    odm_client.connect()
    user = odm_client.get_instances(NEOUSER_TYPE_MODEL_NAME, username=request.user.username)[0]

    loved = [news["link"] for news in odm_client.get_children(user["uuid"], LOVES_IT_RELATION)]

    odm_client.disconnect()

    return HttpResponse(json.dumps(loved))


@utils.error_writing
@utils.timed
def loved_it(request):
    if 'uuid' not in request.GET:
        raise Exception("Not passed UUID to loved_it view")


    odm_client = ODMClient()
    odm_client.connect()

    user = odm_client.get_instances(NEOUSER_TYPE_MODEL_NAME, username=request.user.username)[0]
    news = odm_client.get_by_uuid(node_uuid=request.GET['uuid'])

    #TODO: it is just unbelivabely naive way to do it, rewrite in next iteration
    #idea : bloomfilters in odm_server (related_bloomfilter)
    #cool idea btw
    loved = [n["link"] for n in odm_client.get_children(user["uuid"], LOVES_IT_RELATION)]


    if news["link"] in loved:
        return HttpResponse(json.dumps({}))

    odm_client.set(node_uuid=news["uuid"], node_params={"loved_counter": news["loved_counter"] + 1})
    odm_client.add_rel(start_node_uuid=user["uuid"], end_node_uuid=news["uuid"], rel_type=LOVES_IT_RELATION)

    odm_client.disconnect()

    return HttpResponse(json.dumps({}))


@utils.error_writing
@utils.timed
def unloved_it(request):
    odm_client = ODMClient()
    odm_client.connect()


    user = odm_client.get_instances(NEOUSER_TYPE_MODEL_NAME, username=request.user.username)[0]
    news = odm_client.get_by_uuid(node_uuid=request.GET['uuid'])

    odm_client.set(node_uuid=news["uuid"], node_params={"loved_counter": news["loved_counter"] - 1})
    odm_client.del_rel(start_node_uuid=user["uuid"], end_node_uuid=news["uuid"], rel_type=LOVES_IT_RELATION)

    return HttpResponse(json.dumps({}))


import sys
# TODO: better than is_authenticated, but we need a login page: @login_required(login_url='/accounts/login/')
@utils.timed
@utils.error_writing
def graph_view_all_subscribed(graph_view_descriptor, graph_display_descriptor):
    """
        @param graph_view_descriptor now represented as dictionary. We have to design it more carefully
    """
    try:
        odm_client = ODMClient()
        odm_client.connect()

        content_items_array = []  # building news to be rendered (isn't very efficient..)

        user = odm_client.get_instances(NEOUSER_TYPE_MODEL_NAME, username=graph_display_descriptor["username"])[0]

        #TODO: pick only most recent loved it
        #TODO: it is very heavily prototyped, move to separate graph view
        loved = [news["link"] for news in odm_client.get_children(user["uuid"], LOVES_IT_RELATION)]

        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        # Get news for authenticated users.


        for content_source in odm_client.get_children(user["uuid"], SUBSCRIBES_TO_RELATION):
            for content in odm_client.get_children(content_source['uuid'], PRODUCES_RELATION):
                content['loved'] = int(content['link'] in loved)
                content['color'] = colors[random.randint(0, 4)]

                content_items_array.append(content)


        category_array = get_category_array(graph_view_descriptor)

        odm_client.disconnect()

        page_size = 20
        if 'page' in graph_display_descriptor:
            page = int(graph_display_descriptor['page'])
            page_size = int(graph_display_descriptor['page_size'])



        a = page * page_size
        if a < len(content_items_array):
            b = (page + 1) * page_size
            if b <= len(content_items_array):
                content_items_array = content_items_array[a:b]
            else:
                content_items_array = content_items_array[a:]
        else:
            content_items_array = []


    except Exception, e:
        print "Exception in graph_view_all_subscribed : ", e
        return {}



    return content_items_array


#TODO: move to ocean_master
@utils.error_writing
def get_graph(graph_view_descriptor, graph_display_descriptor, start, end):
    """
        This function returns graph that will be rendered by GraphDisplay
        (old rss_items)

        @param graph_view_descriptor Descriptor specyfing GraphView to be fetched
        @param graph_display_descriptor Descriptor specyfing GraphDisplay that is fetching
        @param start integer

    """

    # Construct appropriate graph_view (@note: will be moved to OceanMaster)
    if "name" in graph_view_descriptor:

        if graph_view_descriptor["name"] == "Subscribed":
            return  graph_view_all_subscribed(graph_view_descriptor, graph_display_descriptor)
        elif graph_view_descriptor["name"] == "TrendingNews":
            # Get GraphView (construct if not in cache) from Ocean Master
            gv = OC.construct_graph_view((graph_view_descriptor["name"],
                                          graph_view_descriptor["options"]))

            return gv.get_graph(start, end, graph_display_descriptor)
        else:
            raise Exception("Not recognized graph_view")
    else:
        raise Exception("No name in request")



@utils.view_error_writing
def trending_news(request):
    # Options displayed in GraphDisplay
    options = [
        {"name": "period",
         "list": ["Top week", "Top day", "Top hour!"],
         "state": 0,
         "action": "rewrite_display"}
    ]

    graph_display_descriptor = {}
    graph_display_descriptor["name"] = "ListDisplay"
    graph_display_descriptor["options"] = options
    graph_display_descriptor["title"] = "TRENDING NEWS"
    graph_display_descriptor["likeable"] = 0
    graph_display_descriptor["page"] = 0
    graph_display_descriptor["page_size"] = 20
    graph_display_descriptor["username"] = request.user.username

    # Setup options
    option_dict = {}
    for opt in options:
        option_dict[opt["name"]] = opt["state"]

    # Get graph using default graph_view_descriptor
    graph_view_descriptor = {"name": "TrendingNews",
                               "options": option_dict}

    rss_items = get_graph(graph_view_descriptor, graph_display_descriptor, \
                          graph_display_descriptor["page"],\
                          graph_display_descriptor["page_size"]
                          )
    # Construct List Display Descripor
    data = {}



    data["graph_view_descriptor"] = json.dumps(graph_view_descriptor)
    data["graph_display_descriptor"] = json.dumps(graph_display_descriptor)
    data["signed_in"] = True
    data["categories"] = get_category_array(graph_view_descriptor)

    data["likeable"] = graph_display_descriptor["likeable"]
    #TODO: why I cannot do graph_display_descriptor.likeable?
    data["rss_items"] = rss_items
    return utils.render(request, 'rss/index.html', data)


@utils.view_error_writing
def index(request):
    graph_display_descriptor = {}
    graph_display_descriptor["name"] = "ListDisplay"
    graph_display_descriptor["options"] = []
    graph_display_descriptor["title"] = "TRENDING NEWS"
    graph_display_descriptor["likeable"] = 1
    graph_display_descriptor["sortable"] = 1
    graph_display_descriptor["page"] = 0
    graph_display_descriptor["page_size"] = 20
    graph_display_descriptor["username"] = request.user.username


    # Get graph using default graph_view_descriptor
    graph_view_descriptor = {"name": "Subscribed",
                               "options": {}}

    rss_items = get_graph(graph_view_descriptor, graph_display_descriptor, \
                          graph_display_descriptor["page"],\
                          graph_display_descriptor["page_size"]
                          )

    # Construct List Display Descripor
    data = {}
    data["graph_view_descriptor"] = json.dumps(graph_view_descriptor)
    data["graph_display_descriptor"] = json.dumps(graph_display_descriptor)
    data["signed_in"] = True
    data["categories"] = get_category_array(graph_view_descriptor)
    data["rss_items"] = rss_items
    data["sortable"] = 1

    data["likeable"] = graph_display_descriptor["likeable"]
    #TODO: why I cannot do graph_display_descriptor.likeable?
    return utils.render(request, 'rss/index.html', data)







def get_rss_channels(request):
    """Get subscribed RSS channels list from databasa."""
    if request.user.is_authenticated():
        content_items_array = []  # building news to be rendered (isn't very efficient..)
        odm_client = ODMClient()
        odm_client.connect()
        user = odm_client.get_instances(NEOUSER_TYPE_MODEL_NAME, username=request.user.username)[0]
        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']
        for content_source in odm_client.get_children(user["uuid"], "subscribes_to"):
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

        odm_client.disconnect()
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
    rss_items = get_graph(json.loads(request.GET['graph_view_descriptor']),
                     json.loads(request.GET['graph_display_descriptor']
                     ),
                     start=int(request.GET['start']),
                     end=int(request.GET['end']))

    render_dict = {
        "rss_items" : rss_items,
        "graph_display_descriptor" : json.loads(request.GET['graph_display_descriptor']),
        "likeable" : json.loads(request.GET['graph_display_descriptor'])["likeable"]
    }

    if len(rss_items) > 0:
        return utils.render(request, 'rss/list_display_renderer.html', render_dict)
    else:
        return HttpResponse(content="fail", content_type="text/plain")


@utils.view_error_writing
def add_content_source(request):
    if request.user.is_authenticated():

        odm_client = ODMClient()
        odm_client.connect()

        user = odm_client.get_instances(NEOUSER_TYPE_MODEL_NAME, username=request.user.username)[0]


        is_subscribed = False
        #TODO: Think about caching things like that?
        for content_source in odm_client.get_children(user["uuid"], 'subscribes_to'):
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

            odm_client.add_rel(user["uuid"], content_source["uuid"], "subscribes_to")

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


def news_preview(request):
    url = request.GET['url']
    return utils.render(request, 'base/news_preview.html', {'url': url})
