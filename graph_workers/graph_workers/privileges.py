"""
Privileges represented as hierarchical structure
Every object is passed part of it

Note : prototyped only
"""
#TODO: implement fully

import copy

"""
System design
==========

1. Actors
-----

Main actors in our system are :

* **Graph Worker** - adding new data to our graph. Graph Workers have
certain privileges, should be possible to be run across multiple machines. Graph Worker only adds new information to graph, doesn't display anything and doesn't prepare data for displaying. Graph Workers are independent from Django/webservice. Are very likely to be written in Scala, or C++.

    Example in our system : news_fetcher


* **Graph View** - think of Graph View as of database view. It is an object that provides data (technically igraph) for later displaying. The different from regular database view is that they support functionality like updates and more complicated query.

    No examples in our system yet ! Closest example we have are functions in rss/view.py .

* **Graph Display** - finally this is displaying igraph received from Graph View. Important thing to note is that it is completely passive, in that sense that it doesn't modify or even contact the Graph View.

    Example in our system: list display of news.


2. Graph database description
---------

Nodes types:

* **NeoUser** - for making queries simpler
    * label
    * username


* **NewsWebsite** (note: this name is likely to be changed, or it will be a subclass of ContestSource) - linked by NeoUser by "subscribes"
    * label - alway equal to "__news__"
    * title
    * image_width - ?
    * image_height - ?
    * image_link - ?
    * image_url -?
    * last_updated - last time visited by news_fetcher

* **News** - linked by NewsWebsite by "produces"
    * label
    * title
    * link
    * description
    * language
    * last_updated - last time added/modified by news_fetcher
"""



PRIVILEGE_WRITE = 1
PRIVILEGE_READ = 0

root = {"NewsWebsite": None, "News": None, "NeoUser": None}


root["NewsWebsite"] = {"label": PRIVILEGE_WRITE,
                       "description": PRIVILEGE_WRITE,
                       "image_width": PRIVILEGE_WRITE,
                       "image_height": PRIVILEGE_WRITE,
                       "image_link": PRIVILEGE_WRITE,
                       "image_url": PRIVILEGE_WRITE,
                       "language": PRIVILEGE_WRITE,
                       "last_updated": PRIVILEGE_WRITE
                       }

root["News"] = {"label": PRIVILEGE_WRITE,
                "link": PRIVILEGE_WRITE,
                "title": PRIVILEGE_WRITE,
                "description": PRIVILEGE_WRITE,
                "guid": PRIVILEGE_WRITE,
                "last_updated": PRIVILEGE_WRITE
                }



def construct_full_privilege():
    """ Get full privilege object """
    return copy.deepcopy(root)

def privileges_bigger_or_equal(privilege, needed_privilege):
    """ Try if is ok <=> All entries are bigger or equal """
    #TODO: implement
    return True