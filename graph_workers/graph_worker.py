"""
Specifies GraphWorker interface.
Defines metadata that can be passed to GraphWorker
"""


"""
TODO: Think about implementing GraphWorkers in C++
lots of work - problems with implementing wrappers over neo4j
maybe Scala is the way to go? discuss..

I will leave Scala discussion for 3rd iteration.

Coding prototype in python will be useful for testing the architecture
"""


class GraphWorker(object):
    def get_required_privileges(self):
        """
            @returns List of required privileges
        """
        raise NotImplementedError()

    def attach_logger(self, logger):
        """
            @param python logger object (supports log, info, warning)
        """

    @staticmethod
    def create_master(self, **params):
        """
            @param **params - parameters passed to the constructor
            @returns Descriptor of master (used in create_worker) and GraphWorker object
        """
        raise NotImplementedError()

    @staticmethod
    def create_worker(self, master_descriptor, **params):
        """
            @param **params - parameters passed to the constructor
            @returns GraphWorker object
        """
        raise NotImplementedError()


    def run(self):
        """
            Parameterless run of GraphWorker object. Should branch on being master or worker
        """
        raise NotImplementedError()