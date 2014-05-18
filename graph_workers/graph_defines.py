"""
This file defines constants used in graph operations
"""


### Default dictionaries for all models in the graph ###
#TODO: add all fields
CONTENT_MODEL = {"loved_counter": 0, "last_updated": 0, "pubdate_timestamp": 0}
GRAPH_MODELS = {"Content":CONTENT_MODEL}


CONTENT_SOURCE_LAST_UPDATE = "last_updated"
CONTENT_SOURCE_LINK = "link"
CONTENT_SOURCE_RSS_TYPE = "source_type"

CONTENT_PUBDATE_TIMESTAMP = "pubdate_timestamp"
CONTENT_PUBDATE = "pubdate"


HAS_TYPE_RELATION = '<<TYPE>>'
HAS_INSTANCE_RELATION = '<<INSTANCE>>'
HAS_TAG_RELATION = '<<TAG>>'
HAS_FEED_RELATION = '<<FEED>>'
HAS_INCLUDES_RELATION = '<<INCLUDES>>'
HAS_EXCLUDES_RELATION = '<<EXCLUDES>>'
SUBSCRIBES_TO_RELATION = "subscribes_to"
PRODUCES_RELATION = "__produces__"
LOVES_IT_RELATION = "__loves_it__"
# Website __has__ ContentSource relation:
HAS_RELATION = "__has__"

#root = graph_db.node(0)

TAG_TYPE_MODEL_NAME = 'Tag'
CONTENT_TYPE_MODEL_NAME = "Content"
NEOUSER_TYPE_MODEL_NAME = "NeoUser"
NEWS_WEBSITE_TYPE_MODEL_NAME = "NewsWebsite"
WEBSITE_TYPE_MODEL_NAME = 'Website'
CONTENT_SOURCE_TYPE_MODEL_NAME = 'ContentSource'

FEED_TYPE_NAME = 'Feed'

