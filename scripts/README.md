/scripts
========

ocean_small_exemplary_data.py
-----------------------------

This script will erase whole graph database and will populate it with a few
exemplary nodes.

ocean_exemplary_data.py
-----------------------

With this script graph database will be erased and `ContentSource` node
dictionaries from `../data/contentsource_nodes_exemplary` (default) will be
added.

You can get `contentsource_nodes_exemplary` file from Ocean Don Corleone server
or generate it yourself with `../graph_workers/spidercrab_slave.py` (run
this script with `-h` option for details) or
`/graph_workers/web_crawler_export.py` (run this script for details).

Try using `contentsource_nodes_1` if you want big data base (also on Ocean
Don Corleone server).

ocean_init_graph.py
-------------------

This script initializes graph with default data, needed to start working with
a database and/or Lionfish (creates meta-nodes).

NOTE: Creates root node (0) if not present :)

NOTE: This script is used by above scripts.

