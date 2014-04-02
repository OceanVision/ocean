#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    SpiderCrab - simple, synchronized news fetching GraphWorker
"""
import boilerpipe.extract
import feedparser
import multiprocessing
import os
import shutil
import threading

from graph_workers.graph_utils import *
from graph_workers.graph_worker import GraphWorker
from graph_workers.privileges import construct_full_privilege
from odm_client import ODMClient

SOURCES_ENQUEUE_PORTION = 10
SOURCES_ENQUEUE_MAX = float('inf')
WORKER_SLEEP_S = 1

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
        self.workers = []

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
        master.workers.append(spidercrab_worker)
        logger.log(info_level, '... Created Spidercrab worker.')
        return spidercrab_worker

    def run(self):
        """
            Parameter-less run of GraphWorker object.
            You should run master Spidercrab only.
            (workers are run by adequate master)
        """
        self._init_run()

        if self.is_master:
            self._run_local_workers()
            queued_sources = 0
            while queued_sources < self.config['sources_enqueue_max']:
                # Enqueue new sources to be browsed by workers
                result = self._enqueue_sources_portion()
                queued_sources += len(result)
                if len(result) == 0 or self.terminate_event.is_set():
                    break

        else:  # worker case
            time.sleep(WORKER_SLEEP_S)
            while not self.terminate_event.is_set():
                source = self._pick_pending_source()
                if len(source) > 0:
                    self._update_source(source)
                else:
                    break

        self._end_run()

    def _init_run(self):
        self.odm_client.connect()

        if self.is_master:
            logger.log(
                info_level,
                'Started running "' + self.config['worker_id'] +
                '" master Spidercrab.'
            )
        else:
            logger.log(
                info_level,
                'Started running "' + self.config['worker_id'] +
                '" worker (slave) Spidercrab.'
            )
            return

        # Check database structure and init if needed
        self._check_and_init_db()

        # Register our spidercrab instance in db if not registered
        self._check_and_register()

    def _end_run(self):
        self.odm_client.disconnect()
        if self.is_master:
            logger.log(
                info_level,
                'Spidercrab "' + self.config['worker_id'] +
                '" master finished!'
            )
        else:
            logger.log(
                info_level,
                'Spidercrab "' + self.config['worker_id'] +
                '" worker (slave) finished!'
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
            ids.append(instance['worker_id'])
        if self.config['worker_id'] in ids:
            self.logger.log(
                info_level,
                'Spidercrab ' + self.config['worker_id']
                + ' already registered in the database.'
            )
        else:
            self.logger.log(
                info_level,
                'Registering ' + self.config['worker_id']
                + ' Spidercrab in the database.'
            )
            params = {
                'model_name': 'Spidercrab'
            }
            params.update(self.config)
            self.odm_client.create_node(
                **params
            )

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
        self.config = dict(json.load(open(self.CONFIG_FILE_NAME)))

        # Required preferences
        assert 'update_interval_min' in self.config
        assert 'use_all_sources' in self.config
        assert 'content_sources' in self.config
        assert 'worker_id' in self.config

        # Optional preferences
        if 'sources_enqueue_portion' not in self.config:
            self.config['sources_enqueue_portion'] = SOURCES_ENQUEUE_PORTION
        if 'sources_enqueue_max' not in self.config:
            self.config['sources_enqueue_max'] = SOURCES_ENQUEUE_MAX

        if self.config['worker_id'] == 'UNDEFINED':
            raise ValueError(
                'Please choose your id and enter it inside '
                + self.CONFIG_FILE_NAME + '!'
            )

    def _run_local_workers(self):
        """
            Run workers associated with this master.
        """
        processes = []
        for worker in self.workers:
            processes.append(multiprocessing.Process(target=worker.run))
        for p in range(len(processes)):
            processes[p].start()

    def _enqueue_sources_portion(self):
        """
            Fetch <sources_enqueue_portion> sources and immediately assign
            them 'pending' relation with own Spidercrab node. Method used by
            master.
        """
        query = """
        MATCH
            (source:ContentSource),
            (crab:Spidercrab {worker_id: '%s'})
        WHERE NOT source-[:pending]-crab
        CREATE (crab)-[:pending]->(source)
        RETURN source
        LIMIT %s
        """
        query %= (
            self.config['worker_id'],
            self.config['sources_enqueue_portion'],
        )
        result = self.odm_client.execute_query(query)
        return result

    def _pick_pending_source(self):
        """
            Pick first free ContentSource (pending in master Spidercrab node),
            remove pending rel and mark it as updated. Method used by workers.
        """
        query = """
        MATCH
            (crab:Spidercrab {worker_id: '%s'})
            -[r:pending]->
            (source:ContentSource)          //TODO: Add test if time passed
        SET source.last_updated = %s
        DELETE r
        RETURN source
        LIMIT 1
        """
        query %= (
            self.config['worker_id'],
            database_gmt_now(),
        )
        result = self.odm_client.execute_query(query)
        if len(result) > 0:
            return result[0][0]
        else:
            return {}

    def _update_source(self, source_node):
        """
            Update params of given node (a dict with 'uuid' and 'link' keys)
        """
        feed = self._parse_source(source_node['link'])
        query = """
        MATCH (source:ContentSource {uuid: %s})
        SET
            source.language = '%s',
            source.title = '%s',
            source.description = '%s',
            source.source_type = '%s',
        RETURN source
        """
        query %= (
            source_node['uuid'],
            feed['language'],
            feed['title'],
            feed['description'],
            feed['source_type']
        )
        result = self.odm_client.execute_query(query)

    @staticmethod
    def _parse_source(source_link):
        """
            Parse source properties to a dictionary using various methods.
            (For later use with methods for other further content sources)
        """
        data = feedparser.parse(source_link)
        result = dict()
        result['language'] = data['feed']['language']
        result['title'] = data['feed']['title']
        result['description'] = data['feed']['description']
        result['source_type'] = 'rss'
        result['news'] = []
        for entry in data['entries']:
            news = dict()
            news['title'] = entry['title']
            news['summary'] = entry['summary']
            news['link'] = entry['link']
            result['news'].append(news)
        return result


if __name__ == '__main__':
    spidercrab = Spidercrab.create_master()
    Spidercrab.create_worker(spidercrab)
    Spidercrab.create_worker(spidercrab)
    Spidercrab.create_worker(spidercrab)
    spidercrab.run()