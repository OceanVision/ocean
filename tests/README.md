Database manager (Lionfish) unit tests
=======================================
Some of the results need to be verified with py2neo library.

get_by_uuid:
* 2x correct uuid for various models
* 1x incorrect
* 1x multiple with batch

get_by_link:
* 2x correct uuid for various models
* 1x incorrect
* 1x multiple with batch

get_model_nodes:
* 1x regular

get_children:
* 1x not empty
* 1x not empty with parameters
* 1x empty
* 1x multiple with batch

get_instances:
* 1x not empty
* 1x empty
* 1x multiple with batch

set:
* 1x correct uuid
* 1x incorrect uuid
* 1x multiple with batch

create_node & delete_node:
* 1x correct model name
* 1x incorrect model name
* 1x multiple with batch

create_relationship & delete_relationship:
* 1x correct model name
* 1x incorrect model name
* 1x multiple with batch
