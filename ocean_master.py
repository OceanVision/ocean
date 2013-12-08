""" This is a prototype for OceanMaster object.

We will se how it works in practice and modify it in an agile way
"""


class OceanMaster(object):
    """ Ocean master - every important call should go through this object

    """
    def __init__(self):
        pass



    def construct_graph_view(self, graph_view_expression):
        """
        Checks in cache if this graph_view is already constructed.

        If not it constructs it using graph_view_expression
        """
        #1. Check cache
        #2. If not present - construct
        pass

    def get_content(self, graph_view_expression, graph_display_expression):
        """

        Get content (igraph) based on expressions
        for GraphView and GraphDisplay.

        @note: The ultimate goal is to define a language over GraphViews and GraphDisplays
        based on JSON. It is a good idea in my opinion

        @param graph_view_expression Graph View expression
        @param graph_display_expression Graph Display expression
        """
        #1. Construct graph display
        #2. Construct graph view
        #3. Check if the returning type is ok for graph display
        #4.
        pass


OC = OceanMaster()