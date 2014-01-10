"""
This file defines constants used in graph operations
"""


CONTENT_SOURCE_LAST_UPDATE = "last_updated"
CONTENT_SOURCE_LINK = "link"
CONTENT_SOURCE_RSS_TYPE = "source_type"

CONTENT_PUBDATE_TIMESTAMP = "pubdate_timestamp"
CONTENT_PUBDATE = "pubdate"


HAS_TYPE_RELATION = "<<TYPE>>"
HAS_INSTANCE_RELATION = "<<INSTANCE>>"
SUBSCRIBES_TO_RELATION = "__subscribes_to__"
PRODUCES_RELATION = "__produces__"
LOVES_IT_RELATION = "__loves_it__"
# Website __has__ ContentSource relation:
HAS_RELATION = "__has__"

#root = graph_db.node(0)


CONTENT_TYPE_MODEL_NAME = "Content"
NEOUSER_TYPE_MODEL_NAME = "NeoUser"
NEWS_WEBSITE_TYPE_MODEL_NAME = "NewsWebsite"
WEBSITE_TYPE_MODEL_NAME = 'Website'
CONTENT_SOURCE_TYPE_MODEL_NAME = 'ContentSource'

