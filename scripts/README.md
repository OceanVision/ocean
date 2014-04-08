/scripts
========

ocean_exemplary_data.py
-----------------------

With this script graph database will be erased and ContentSource node
dictionaries from `/data/content_sources` (default) file will be added.

You can get `content_sources` file from Ocean Don Corleone server or generate
it yourself with `/graph_workers/spidercrab_slaves.py` or
`/graph_workers/web_crawler_export.py` (run those scripts for details).

ocean_init_graph.py
-------------------

This script initializes graph with default data, needed to start working with
a database and/or Lionfish (creates meta-nodes).
NOTE: Creates root node (0) if not present :)

ocean_small_exemplary_data.py
-----------------------------

This script will erase whole graph database and will populate it with a few
exemplary nodes.