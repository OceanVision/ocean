# Ocean Admin

Ocean admin is a server that can be used to easily admin the Ocean cluster
or check Ocean status, etc. run_node script is an easy way to join our node
to the cluster. In case of failure (repeatiting responsibilities etc.) it
should inform you about the problem. run_node will run all the services and register the node. You should not
run services yourself!

Sidenote: For checking Hadoop cluster status we will use Hue service (included in Cloudera package).


### Configuration file

You have to specify following items:

* master: ip or domain of the master node, if you want to run locally everything just set it to "local"

* responsibilties: what responsibilities is this node registering. Options:

    * neo4j

    * news_fetcher_master (not implemented, pending)

    * news_fetcher_slave (not implemented, pending, can specify many slaves)

    * web_crawler_master (implemented, but not as a service)

    * web_crawler_slave (implemented, but not as a service, can specify many slaves)

    * web_service

    * odm

    * puffer (not implemented, main backend service running jobs on hadoop, etc.)

    * hadoop_cluster_master (not implemented)

    * hadoop_cluster_slave (not implemented)

    * kafka (not implemented)

Each responsibility is a list of name and running command (or just name, if default
running command is sufficient)

* home: path to your ocean directory

### Running

`python run_node.py` should run node accordingly to the configuration file. If it is
a master it will run the master service. And for every configuration it will register
to the master responsibilities.


### Fetching configuration

The main idea is that modules can fetch configuration from the webserivce. The function
is defined in ocean_admin/utils.py

Usage: fetch_configuration(name), where name is a string, one of the following:

* neo4j_address (will fetch ip or domain)

* neo4j_port

* odm_address

* odm_port

* news_fetcher_master_address

Function returns a JSON, in our case it will be in most cases a string.


### Stoping

Hit ctrl+C , run_node.py should terminate the responsibilities and deregister.

### Administrating

Go to <master>:8881  , and you should see webservice with intuitive UI for administrating Ocean.