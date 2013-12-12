"""
This file defines constants used in graph operations
"""


NEWS_WEBSITE_LAST_UPDATE = "last_updated"
NEWS_WEBSITE_LINK = "link"
NEWS_WEBSITE_RSS_TYPE = "source_type"

NEWS_PUBDATE_TIMESTAMP = "pubdate_timestamp"
NEWS_PUBDATE = "pubdate"


HAS_TYPE_RELATION = "<<TYPE>>"
HAS_INSTANCE_RELATION = "<<INSTANCE>>"
SUBSCRIBES_TO_RELATION = "__subscribes_to__"
PRODUCES_RELATION = "__produces__"
LOVES_IT_RELATION = "__loves_it__"
# Website __has__ ContentSource relation:
HAS_RELATION = "__has__"

#root = graph_db.node(0)


NEWS_TYPE_MODEL_NAME = "News"
NEOUSER_TYPE_MODEL_NAME = "NeoUser"
NEWS_WEBSITE_TYPE_MODEL_NAME = "NewsWebsite"
WEBSITE_TYPE_MODEL_NAME = 'Website'
CONTENT_SOURCE_TYPE_MODEL_NAME = 'ContentSource'

