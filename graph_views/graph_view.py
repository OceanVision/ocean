#import ocean_master


from graph_utils import database_timestamp_to_datetime, GMTdatetime_to_database_timestamp, get_datetime_gmt_now
import datetime
from neo4j_wrapper import get_records_from_cypher
import random
from rss.models import *

from py2neo import neo4j


class GraphView(object):
    """ Abstract class for GraphView """

    def __init__(self):
        #We have to define update_frequency_s
        pass


    def update(self):
        pass

    def get_graph(self, graph_display):
        """
        Constructs graph that will be displayed
        @param graph_display Object representing graph_display (agile currently, like string or sth)
        """
        raise NotImplementedError()

    # Not required for now
    #def get_graph_view_expression(self):
    #    """ Return (class, dict_args) """
    #    raise NotImplementedError()


class TestingGV(GraphView):
    def get_graph(self):
        return []

    def __init__(self, arg1, arg2, arg3):
        self.update_frequency_s = 10






class TrendingNews(GraphView):
    """
        Basic GraphView for fetching Trending News (that is popular and new)
        First sorted by likes, then sorted by publication date
    """

    period_options = ["Week", "Day"]

    def get_graph(self, graph_display):
        if "page_size" in graph_display:

            if 'page' in graph_display:
                page = int(graph_display['page'])
                page_size = int(graph_display['page_size'])

            a = page * page_size
            if a < len(self.prepared_view):
                b = (page + 1) * page_size
                if b <= len(self.prepared_view):
                    return self.prepared_view[a:b]
                else:
                    return self.prepared_view[a:]

            return []
        else:
            return self.prepared_view

    def update(self):
        print "Updating  TrendingNews ", self.period
        #TODO : Improve efficiency

        dt_threshold = None
        if TrendingNews.period_options[self.period] == "Week" :
            dt_threshold = get_datetime_gmt_now() - datetime.timedelta(days=7)
        elif TrendingNews.period_options[self.period] == "Day":
            dt_threshold = get_datetime_gmt_now() - datetime.timedelta(days=1)

        timestamp = GMTdatetime_to_database_timestamp(dt_threshold)

        # TODO:
        # This query looks at every node in the graph, right : not the best idea
        # Solution : index over timestamp (quite easy to do in neo4j - investigate and measure performance)

        cypher_query = """
            START root=node(0)
            MATCH root-[rel:`<<TYPE>>`]->news_type-[rel2:`<<INSTANCE>>`]->news
            WHERE news_type.name="rss:News" and news.pubdate_timestamp > { timestamp }
            RETURN news
            ORDER BY news.pubdate_timestamp DESC
            LIMIT 100
        """


        #user.refresh()
        #loved = [news.link for news in user.loves_it.all()]

        fetched_news = [r.news for r in
                        get_records_from_cypher(neo4j.GraphDatabaseService("http://localhost:7474/db/data/"),
                                      cypher_query, {"timestamp": timestamp})]

        self.prepared_view = [] #TODO: use previous results
        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']

        for news in fetched_news:
            news_dict = {}
            news_dict['pk'] = news._id
            news_dict['loved'] = 0 #TODO: repair
            news_dict.update(
                {'title': news["title"], 'description': news["description"], 'link': news["link"],
                 'pubDate': news["pubdate"], 'category': 2})
            news_dict['color'] = colors[random.randint(0, 4)]
            self.prepared_view.append(news_dict)

        #sort them

        print "Update successful"

    def __init__(self, period ):
        self.period = period
        self.update_frequency_s = 10
        self.prepared_view = []