#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    SpiderCrab - simple news fetching GraphWorker
"""

import threading

from ..graph_defines import *
from ..graph_utils import logger as graph_utils_logger
from ..graph_worker import GraphWorker
from ..odm_client import ODMClient
from ..privileges import construct_full_privilege


class Spidercrab(GraphWorker):
    logger = graph_utils_logger
    required_privileges = construct_full_privilege()
    odm_client = ODMClient()
    terminate_event = threading.Event()

    def __init__(self, master=None):
        pass

    def terminate(self):
        """
            terminates self thread and returns
        """
        self.terminate_event.set()

    def get_required_privileges(self):
        """
            @returns List of required privileges
        """
        return self.required_privileges

    def attach_logger(self, new_logger):
        """
            @param new_logger - Python logger object (supports log, info,
            warning)
        """
        self.logger = new_logger

    @staticmethod
    def create_master(self, **params):
        """
            @param **params - parameters passed to the constructor
            @returns master (used in create_worker)
        """
        self.logger.info('Creating Spidercrab master...')
        return Spidercrab(**params)

    @staticmethod
    def create_worker(self, master, **params):
        """
            @param master - master Spidercrab object
            @param **params - parameters passed to the constructor
            @returns GraphWorker object
        """
        if len(params) < 1:
            raise Exception("Wrong param list")
        self.logger.info('Creating Spidercrab worker...')
        params['master'] = master
        return Spidercrab(**params)

    def run(self):
        """
            Parameter-less run of GraphWorker object.
        """
        raise NotImplementedError()
