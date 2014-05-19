"""
File defines constants used by don corleone. Modify to reflect your needs.

TODO: load from file
"""

UPDATE_FREQ = 10
KILL_NODE_COUNTER = 1000*60 / (1000*UPDATE_FREQ) # Kill not answering server if doesn't answer for 60s
CONFIG_DIRECTORY = "config"
OK = "ok"

CLIENT_CONFIG_PORT = "port"
CLIENT_CONFIG_HOME = "home"
CLIENT_CONFIG_SSH_USER = "ssh-user"
CLIENT_CONFIG_SSH_HOST = "public_ssh_domain"
CLIENT_CONFIG_SSH_PORT = "ssh-port"

CONFIG_DEFAULT_SERVICE_PARAMS = "default_service_params"
CONFIG_ADDS = "adds"
CONFIG_DEPENDS = "depends"
CONFIG_ARGUMENTS = "arguments"
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
SERVICE_LIONFISH_SCALA = "lionfish_scala"
SERVICE_MANTIS_SHRIMP_MASTER = "mantis_shrimp_master"
SERVICE_MANTIS_SHRIMP = "mantis_shrimp"

KNOWN_SERVICES = set([SERVICE_LIONFISH,  SERVICE_NEO4J,
                      SERVICE_KAFKA, SERVICE_ZOOKEEPER, SERVICE_SPIDERCRAB_MASTER,\
                      SERVICE_SPIDERCRAB_SLAVE, SERVICE_TEST_SERVICE,
                      SERVICE_LIONFISH_SCALA, SERVICE_MANTIS_SHRIMP_MASTER,
                      SERVICE_MANTIS_SHRIMP

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
SERVICE_AS_ADDED = "is_added" # If added by another service - cannot be run/terminated
#Without http
SERVICE_HOME = "home"
SERVICE_PORT = "port"
SERVICE_RUN_CMD = "run_cmd"
SERVICE_NAME = "service"
SERVICE_PARAMETERS = "service_params" # Additional service parameters
SERVICE_CONFIG = "service_config" # Service config for given service, normally copied from config/* directory
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



#TODO: move to utils

import threading

__author__ = "Mateusz Kobos"

class RWLock:
	"""Synchronization object used in a solution of so-called second
	readers-writers problem. In this problem, many readers can simultaneously
	access a share, and a writer has an exclusive access to this share.
	Additionally, the following constraints should be met:
	1) no reader should be kept waiting if the share is currently opened for
		reading unless a writer is also waiting for the share,
	2) no writer should be kept waiting for the share longer than absolutely
		necessary.

	The implementation is based on [1, secs. 4.2.2, 4.2.6, 4.2.7]
	with a modification -- adding an additional lock (C{self.__readers_queue})
	-- in accordance with [2].

	Sources:
	[1] A.B. Downey: "The little book of semaphores", Version 2.1.5, 2008
	[2] P.J. Courtois, F. Heymans, D.L. Parnas:
		"Concurrent Control with 'Readers' and 'Writers'",
		Communications of the ACM, 1971 (via [3])
	[3] http://en.wikipedia.org/wiki/Readers-writers_problem
	"""

	def __init__(self):
		self.__read_switch = _LightSwitch()
		self.__write_switch = _LightSwitch()
		self.__no_readers = threading.Lock()
		self.__no_writers = threading.Lock()
		self.__readers_queue = threading.Lock()
		"""A lock giving an even higher priority to the writer in certain
		cases (see [2] for a discussion)"""

	def reader_acquire(self):
		self.__readers_queue.acquire()
		self.__no_readers.acquire()
		self.__read_switch.acquire(self.__no_writers)
		self.__no_readers.release()
		self.__readers_queue.release()

	def reader_release(self):
		self.__read_switch.release(self.__no_writers)

	def writer_acquire(self):
		self.__write_switch.acquire(self.__no_readers)
		self.__no_writers.acquire()

	def writer_release(self):
		self.__no_writers.release()
		self.__write_switch.release(self.__no_readers)


class _LightSwitch:
	"""An auxiliary "light switch"-like object. The first thread turns on the
	"switch", the last one turns it off (see [1, sec. 4.2.2] for details)."""
	def __init__(self):
		self.__counter = 0
		self.__mutex = threading.Lock()

	def acquire(self, lock):
		self.__mutex.acquire()
		self.__counter += 1
		if self.__counter == 1:
			lock.acquire()
		self.__mutex.release()

	def release(self, lock):
		self.__mutex.acquire()
		self.__counter -= 1
		if self.__counter == 0:
			lock.release()
		self.__mutex.release()