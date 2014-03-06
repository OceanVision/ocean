


class DonCorleoneException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


ERROR_NOT_RUNNING_SERVICE = DonCorleoneException("error_not_running_service_error")
ERROR_ALREADY_REGISTERED_SERVICE = DonCorleoneException("error_already_registered_service")
ERROR_ALREADY_EXISTING_SERVICE = DonCorleoneException("error_already_existing_service")
ERROR_NOT_REGISTERED_SERVICE = DonCorleoneException("error_not_registered_service_error")
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