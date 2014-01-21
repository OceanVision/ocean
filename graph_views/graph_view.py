#import ocean_master


from graph_utils import database_timestamp_to_datetime, GMTdatetime_to_database_timestamp, get_datetime_gmt_now
import datetime
from neo4j_wrapper import get_records_from_cypher
import random
from py2neo import neo4j
from odm_client import ODMClient

class GraphView(object):
    """ Abstract class for GraphView """

    def __init__(self):
        #We have to define update_frequency_s
        pass


    def update(self):
        pass

    def get_graph(self, start=0, end=None, graph_display=None):
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

    period_options = ["Week", "Day", "Hour"]

    def get_graph(self, start=0, end=None, graph_display=None):
        """
        Return subgraph for graph_display
        @param start Starting index
        @param end Ending index
        @param graph_display requesting graph_display
        """
        if end is None: end = len(self.prepared_view) - 1
        if end > len(self.prepared_view):
            end = len(self.prepared_view) - 1
        if start > len(self.prepared_view) or start > end:
            return []


        return self.prepared_view[start:end]

    def update(self):
        dt_threshold = None
        if TrendingNews.period_options[self.period] == "Week" :
            dt_threshold = get_datetime_gmt_now() - datetime.timedelta(days=7)
        elif TrendingNews.period_options[self.period] == "Day":
            dt_threshold = get_datetime_gmt_now() - datetime.timedelta(days=1)
        elif TrendingNews.period_options[self.period] == "Hour":
            dt_threshold = get_datetime_gmt_now() - datetime.timedelta(seconds=60*60)

        #TODO: add checking

        timestamp = GMTdatetime_to_database_timestamp(dt_threshold)

        # TODO:
        # This query looks at every node in the graph, right : not the best idea
        # Solution : index over timestamp (quite easy to do in neo4j - investigate and measure performance)

        # Current solution : separate graph view for each content source - basic graph
        # For now prototyping

        cypher_query = """
            START root=node(0)
            MATCH root-[rel:`<<TYPE>>`]->news_type-[rel2:`<<INSTANCE>>`]->news
            WHERE news_type.model_name="Content" and news.pubdate_timestamp > { timestamp }
            RETURN news
            ORDER BY news.pubdate_timestamp DESC
            LIMIT 100
        """



        fetched_news = [x[0] for x in self.odm_client.execute_query(cypher_query, timestamp=timestamp)
        ] #???

        print "Fetched news ", len(fetched_news)


        preparing_view = [] #TODO: use previous results
        colors = ['ffbd0c', '00c6c4', '74899c', '976833', '999999']


        fetched_news.sort(key=lambda x:
            int(x['pubdate_timestamp'])+
            100000000*int(x['loved_counter']),reverse=True)


        for news in fetched_news:
            news["loved"] = 0 #TODO: repair this
            news["color"] = colors[random.randint(0,4)] #TODO: remove this

        self.prepared_view = fetched_news

        print "Update successful"

    def __init__(self, period ):
        self.period = period
        self.update_frequency_s = 10
        self.prepared_view = []

        self.odm_client = ODMClient()
        self.odm_client.connect()