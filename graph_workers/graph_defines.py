"""
This file defines constants used in graph operations
"""


NEWS_WEBSITE_LAST_UPDATE = "last_updated"
NEWS_WEBSITE_LINK = "link"
NEWS_WEBSITE_RSS_TYPE = "source_type"



USER_LABEL = "__user__"
NEWS_WEBSITE_LABEL = "__news_website__"
NEWS_LABEL = "__news__"

HAS_TYPE_RELATION = "<<TYPE>>"
HAS_INSTANCE_RELATION = "<<INSTANCE>>"
SUBSCRIBES_TO_RELATION = "__subscribes_to__"
PRODUDES_RELATION = "__produces__"


#root = graph_db.node(0)


NEWS_TYPE_MODEL_NAME = "News"
NEOUSER_TYPE_MODEL_NAME = "NeoUser"
NEWS_WEBSITE_TYPE_MODEL_NAME = "NewsWebsite"