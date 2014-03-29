# Don Corleone

Don Corleone is a server that can be used to easily admin the Ocean cluster
or check Ocean status, etc. run_node script is an easy way to join our node
to the cluster. In case of failure (repeatiting responsibilities etc.) it
should inform you about the problem. run_node will run all the services and register the node.
You should not run services yourself!

**Important note**: you can register each service as local, or not. If it is local, then you can
register another instance, and it will be used only by you. If it is global, you cannot
register more than one instance.

Sidenote: For checking Hadoop cluster status we will use Hue service (included in Cloudera package).

**Note**: if you decide not to run don_corleone and not to connect to global
don corleone because you are a strange person - there a mechanism that will
make it work anyway: get_configuration if server is inaccessible with pull your
config from config.json and return values if there is defined service in
node_responsibilities

### Installation

    1. Add file ocean_password to don_corleone folder with your password to ocean
account. Otherwise ocean_don_corleone won't be able to run scripts on your
machine

    2. Configure ssh (as in wiki) - basically add your key from ocean don
       server to your computer and create ssh user with access to your ocean directory.
      **If you want to run locally don** - configure ssh so that you can fire
    for instance ssh staszek@localhost without password prompt.

    3. Prepare config.json file

### Configuration file

Please see config.json : it should explain everything.

You have to specify following items:

* master: url of master

* master_local_url: url of local server (do not change in most cases)

* master_local: true/false : if true, run_node will run don_corleone first

* responsibilties: what responsibilities is this node registering. Options:

    * neo4j

    * **temporary**: news_fetcher

    * news_fetcher_master (not implemented, pending)

    * news_fetcher_slave (not implemented, pending, can specify many slaves)

    * web_crawler_master (implemented, but not as a service)

    * web_crawler_slave (implemented, but not as a service, can specify many slaves)

    * web_service

    * lionfish

    * puffer (not implemented, main backend service running jobs on hadoop, etc.)

    * hadoop_cluster_master (not implemented)

    * hadoop_cluster_slave (not implemented)

    * kafka (not implemented)

Each responsibility is a list of name and additional options.

**Important note**: You add option local: this will make this service local (and accessible only by your computer)

Exemplary additional options.

    * for news_fetcher_slave "id" (default id is 0)

    * for ODM (lionfish) "port" (default port is 7777)

    * for neo4j "port" (default port is 7474)

* home: path to your ocean directory

<few others >

### Running

`python run_node.py` should run node accordingly to the configuration file. If it is
a master it will run the master service. And for every configuration it will register
to the master responsibilities.


### Fetching configuration

The main idea is that modules can fetch configuration from the webserivce. The function
is defined in ocean_admin/utils.py

Usage: fetch_configuration(service_name, config_name). For exemplary usage see lionfish

### Stoping

Hit ctrl+C , run_node.py should terminate the responsibilities and deregister. (Not implemented yet)

### Administrating

Go to 127.0.0.1:8881
