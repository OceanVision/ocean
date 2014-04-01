#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    SpiderCrab - simple news fetching GraphWorker
"""

import boilerpipe.extract
import json
import os
import shutil
import threading

from graph_workers.graph_utils import *
from graph_workers.graph_worker import GraphWorker
from graph_workers.privileges import construct_full_privilege
from odm_client import ODMClient

# Defining levels to get rid of other loggers
info_level = 100
error_level = 200

logging.basicConfig(level=info_level)
logger = logging.getLogger(__name__ + '_ocean')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s \t - %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),
                                           '../logs/spidercrab.log'))
ch_file.setLevel(info_level)
ch_file.setFormatter(formatter)
logger.addHandler(ch_file)


class Spidercrab(GraphWorker):

    DEFAULT_CONFIG_NAME = './spidercrab.json.default'
    CONFIG_FILE_NAME = './spidercrab.json'

    def __init__(
            self,
            master=None,
    ):
        """
        @param master: master Spidercrab object
        @type master: Spidercrab
        """
        self.config = {}
        self._init_config()
        self.logger = logger
        self.required_privileges = construct_full_privilege()
        self.odm_client = ODMClient()
        self.terminate_event = threading.Event()

        self.master = master
        if master:
            assert isinstance(master, Spidercrab)
            self.is_master = False
        else:
            self.is_master = True

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
    def create_master(**params):
        """
            @param **params - parameters passed to the constructor
            @returns master (used in create_worker)
        """
        logger.log(info_level, 'Creating Spidercrab master...')
        spidercrab_master = Spidercrab(**params)
        logger.log(info_level, '... Created Spidercrab master.')
        return spidercrab_master

    @staticmethod
    def create_worker(master, **params):
        """
            @param master - master Spidercrab object
            @param **params - parameters passed to the constructor
            @returns GraphWorker object
        """
        logger.log(info_level, 'Creating Spidercrab worker...')
        if not master:
            raise Exception('Wrong param list!')
        params['master'] = master
        spidercrab_worker = Spidercrab(**params)
        logger.log(info_level, '... Created Spidercrab worker.')
        return spidercrab_worker

    def run(self):
        """
            Parameter-less run of GraphWorker object.
        """
        self._init_run()

        if self.is_master:
            sources = self.odm_client.get_instances('ContentSource')
            print sources

        self._end_run()

    def _init_run(self):
        self.odm_client.connect()

        logger.log(
            info_level,
            'Started running "' + self.config['id'] + '" Spidercrab.'
        )

        if not self.is_master:
            return

        # Check database structure and init if needed
        self._check_and_init_db()

        # Register our spidercrab instance in db if not registered
        self._check_and_register()

    def _end_run(self):
        self.odm_client.disconnect()
        logger.log(
            info_level,
            'Finished running "' + self.config['id'] + '" Spidercrab.'
        )

    def _check_and_init_db(self):
        """
            Checks if Spidercrab meta-nodes are present in the database.
            If not - initializes them.
        """
        # Check if our model is present
        response = self.odm_client.get_model_nodes()
        models = []
        for model in response:
            models.append(model['model_name'])
        if not 'Spidercrab' in models:
            self.logger.log(
                info_level,
                'Spidercrab model not found in the database. Creating...'
            )
            self.odm_client.create_model('Spidercrab')
            self.logger.log(
                info_level,
                'Spidercrab model created.'
            )
        else:
            self.logger.log(
                info_level,
                'Spidercrab model found in the database.'
            )

    def _check_and_register(self):
        """
            Checks if this Spidercrab instance is registered in the database.
            If not - registers it.
        """
        response = self.odm_client.get_instances('Spidercrab')
        ids = []
        for instance in response:
            ids.append(instance['id'])
        if self.config['id'] in ids:
            self.logger.log(
                info_level,
                'Spidercrab ' + self.config['id']
                + ' already registered in the database.'
            )
        else:
            self.logger.log(
                info_level,
                'Registering ' + self.config['id']
                + ' Spidercrab in the database.'
            )
            self.odm_client.create_node('Spidercrab', self.config)

    def _init_config(self):
        """
            Checks if there config file exists and initializes it if needed.
        """
        if not os.path.isfile(self.CONFIG_FILE_NAME):
            shutil.copy(self.DEFAULT_CONFIG_NAME, self.CONFIG_FILE_NAME)
            raise ValueError(
                'Please set up your newly created ' + self.CONFIG_FILE_NAME
                + '!'
            )
        self.config = json.load(open(self.CONFIG_FILE_NAME))
        assert 'update_interval_min' in self.config
        assert 'use_all_sources' in self.config
        assert 'content_sources' in self.config
        assert 'id' in self.config
        if self.config['id'] == 'UNDEFINED':
            raise ValueError(
                'Please choose your id and enter it inside '
                + self.CONFIG_FILE_NAME + '!'
            )


if __name__ == '__main__':
    spidercrab = Spidercrab.create_master()
    spidercrab.run()