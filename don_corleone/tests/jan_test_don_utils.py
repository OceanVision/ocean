if __name__=="__main__":
    import sys, os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    from don_utils import *
    print get_running_service(service_name="spidercrab_master")


    print get_running_service(service_id="neo4j_0",service_config={"port":7777})
    

    services=[ {"service":"x", "service_id":"y", "service_config":{"a":1,"b":2}}]

    print get_service(services, service_id="y", service_config={"a":1}) 

    print "GET CONFIGURATION TESTS"
    print get_configuration_query("port", service_name="neo4j")
    print get_configuration("neo4j","port")
    print get_configuration("neo4j","host")

    print "GET NODE ID"
    print get_my_node_id() 
