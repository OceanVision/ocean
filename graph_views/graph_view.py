#import ocean_master

class GraphView(object):
    """ Abstract class for GraphView """

    def __init__(self):
        #We have to define update_frequency
        pass


    def update(self):
        pass

    def get_graph(self):
        """ Constructs graph that will be displayed """
        raise NotImplementedError()

    # Not required for now
    #def get_graph_view_expression(self):
    #    """ Return (class, args, dict_args) """
    #    raise NotImplementedError()


class TestingGV(GraphView):
    def get_graph(self):
        return []

    def __init__(self, arg1, arg2, arg3):
        self.update_frequency = 1






class TrendingNews(GraphView):
    def get_graph(self):
        return []

    def __init__(self, period_hours, ):
        pass