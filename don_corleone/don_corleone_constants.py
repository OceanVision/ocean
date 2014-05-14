"""
File defines constants used by don corleone. Modify to reflect your needs.

TODO: load from file
"""

UPDATE_FREQ = 1
KILL_NODE_COUNTER = 1000*60 / (1000*UPDATE_FREQ) # Kill not answering server if doesn't answer for 60s
CONFIG_DIRECTORY = "config"
OK = "ok"

CLIENT_CONFIG_PORT = "port"
CLIENT_CONFIG_HOME = "home"
CLIENT_CONFIG_SSH_USER = "ssh-user"
CLIENT_CONFIG_SSH_HOST = "public_ssh_domain"
CLIENT_CONFIG_SSH_PORT = "ssh-port"


CONFIG_DEPENDS = "depends"
CONFIG_PARAMS = "params"
CONFIG_UNARY = "unary"
CONFIG_RUN_SCRIPT = "run_script"
CONFIG_TERMINATE_SCRIPT = "terminate_script"
CONFIG_TEST_SCRIPT = "test_script"


SERVICE_TEST_SERVICE = "test_service"
SERVICE_LIONFISH = "lionfish"
SERVICE_ZOOKEEPER = "zookeeper"
SERVICE_KAFKA = "kafka"
SERVICE_NEO4J = "neo4j"
SERVICE_SPIDERCRAB_MASTER = "spidercrab_master"
SERVICE_SPIDERCRAB_SLAVE = "spidercrab_slave"


KNOWN_SERVICES = set([SERVICE_LIONFISH,  SERVICE_NEO4J,
                      SERVICE_KAFKA, SERVICE_ZOOKEEPER, SERVICE_SPIDERCRAB_MASTER,\
                      SERVICE_SPIDERCRAB_SLAVE, SERVICE_TEST_SERVICE

                      ])


# Read service configs

PARAMETRIZED_SERVICES = set([SERVICE_LIONFISH, SERVICE_SPIDERCRAB_MASTER, SERVICE_SPIDERCRAB_SLAVE])

UNARY_SERVICES = set([ SERVICE_LIONFISH, SERVICE_NEO4J, SERVICE_ZOOKEEPER, SERVICE_KAFKA])

NONUNARY_SERVICES = set([SERVICE_SPIDERCRAB_SLAVE, SERVICE_SPIDERCRAB_MASTER])



SERVICE = "service"
#Service ID is in most cases the same as SERVICE, however if it is local, or if it is multiple_slave it can differ
#For instance hadoop slaves will have service id hadoop_slave:2, whereas local service will have id
#neo4j_local, service id is basically service_name:additional_config ,where service_name can have
#additionally local tag
SERVICE_ID = "service_id"
SERVICE_STATUS = "status"
#Without http
SERVICE_HOME = "home"
SERVICE_PORT = "port"
SERVICE_RUN_CMD = "run_cmd"
SERVICE_NAME = "service"
SERVICE_PARAMETERS = "service_config" # Additional service config
NODE_ID = "node_id" # Id for node
SERVICE_LOCAL = "local"



NODE_RESPONSIBILITIES = "node_responsibilities"
NODE_ADDRESS = "node_address"
NODE_CONFIG = "node_config"
NODE_SSH_HOST = "node_ssh_host"
NODE_SSH_PORT = "node_ssh_port"
NODE_SSH_USER = "node_ssh_user"
NODE_LAST_PING_ANSWER = 0 #time delta to last ping answer.




DEFAULT_COMMAND = "default"
DEFAULT_SSH_PORT = 22
DEFAULT_USER = "ocean"

STATUS_NOTREGISTERED = "not_registered"
STATUS_TERMINATED = "terminated"
STATUS_RUNNING = "running"


class DonCorleoneException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


ERROR_NOT_RUNNING_SERVICE = DonCorleoneException("error_not_running_service_error")
ERROR_ALREADY_REGISTERED_SERVICE = DonCorleoneException("error_already_registered_service")
ERROR_ALREADY_EXISTING_SERVICE = DonCorleoneException("error_already_existing_service")
ERROR_NOT_REGISTERED_SERVICE = DonCorleoneException("error_not_registered_service_error")
ERROR_NOT_REGISTERED_NODE = DonCorleoneException("error_not_registered_service_node")
ERROR_NOT_RECOGNIZED_CONFIGURATION = DonCorleoneException("error_not_recognized_configuration")
ERROR_NOT_REACHABLE_SERVICE = DonCorleoneException("error_not_reachable_service")
ERROR_FAILED_SERVICE_RUN = DonCorleoneException("error_failed_service_run")
ERROR_FAILED_SERVICE_TERMINATE = DonCorleoneException("error_failed_service_terminate")
ERROR_FAILED_SERVICE_DEREGISTER = DonCorleoneException("error_failed_service_deregister")
ERROR_FAILED_SSH_CMD = DonCorleoneException("error_failed_ssh_cmd")
ERROR_SERVICE_ALREADY_RUNNING = DonCorleoneException("error_service_already_running")
ERROR_SERVICE_ALREADY_TERMINATED = DonCorleoneException("error_service_already_terminated")
ERROR_NOT_RECOGNIZED_SERVICE = DonCorleoneException("error_not_recognized_service")
ERROR_SERVICE_ID_REGISTERED = DonCorleoneException("error_service_id_registered")
ERROR_WRONG_METHOD_PARAMETERS = DonCorleoneException("error_wrong_method_parameters")
ERROR_NODE_NOT_REGISTERED = DonCorleoneException("error_node_not_registered")
ERROR = DonCorleoneException("error_not_specified")
ERROR_DUPLICATE = DonCorleoneException("error_duplicate")
ERROR_FILE_NOT_FOUND = DonCorleoneException("error_file_not_found")
ERROR_NOT_SATISFIED_DEPENDENCIES = DonCorleoneException("error_not_satisfied_dependencies")
ERROR_NOT_SATISFIED_DEPENDENCIES_NOT_RUNNING = DonCorleoneException("error_not_satisfied_dependencies_not_running")