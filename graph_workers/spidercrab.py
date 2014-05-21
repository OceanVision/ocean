"""
    Spidercrab - simple, synchronized news fetching GraphWorker
"""

#from BeautifulSoup import BeautifulSoup
import boilerpipe.extract
import feedparser
import json
import os
import shutil
import sys
import threading
import time
import urllib2
import uuid
### TODO: this line shouldn't be here (it worked on Konrad's laptop?) adding toquickly test
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lionfish/python_lionfish/client/'))
from don_corleone import don_utils as du

from graph_workers.graph_defines import *
from graph_workers.graph_utils import *
from graph_workers.graph_worker import GraphWorker
from graph_workers.privileges import construct_full_privilege
from client import Client

# Defining levels to get rid of other loggers
info_level = 100
error_level = 200

logging.basicConfig(level=info_level)
logger = logging.getLogger(__name__ + '_ocean')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),
                                           '../logs/spidercrab.log'))
ch_file.setLevel(info_level)
ch_file.setFormatter(formatter)
logger.addHandler(ch_file)


class Spidercrab(GraphWorker):

    TEMPLATE_CONFIG_NAME = './spidercrab.json.template'
    STANDARD_STATS_EXPORT_FILE = os.path.join(
        os.path.dirname(__file__), '../logs/spidercrab-stats.json')

    # Statistics variable names
    # Master
    S_QUEUED_SOURCES = 'total_queued_sources'
    STATS_DEFAULTS_MASTER = {
        S_QUEUED_SOURCES: 0,
    }
    # Slave
    S_FETCHED_NEWS = 'total_fetched_news'
    S_EXTRACTED_NEWS = 'total_extracted_news'
    S_UPDATED_SOURCES = 'total_updated_sources'
    STATS_DEFAULTS_SLAVE = {
        S_FETCHED_NEWS: 0,
        S_EXTRACTED_NEWS: 0,
        S_UPDATED_SOURCES: 0,
    }

    # Config variable names
    C_UPDATE_INTERVAL_S = 'update_interval_s'
    C_GRAPH_WORKER_ID = 'graph_worker_id'
    C_SOURCES_ENQUEUE_PORTION = 'sources_enqueue_portion'
    C_SOURCES_ENQUEUE_MAX = 'sources_enqueue_max'
    C_NEWS_FETCH_MAX = 'news_fetch_max'
    C_NEWS_FETCH_PER_SOURCE_MAX = 'news_fetch_per_source_max'
    C_MASTER_SLEEP_S = 'master_sleep_s'
    C_SLAVE_SLEEP_S = 'worker_sleep_s'
    C_DO_NOT_FETCH = 'do_not_fetch'
    C_TERMINATE_ON_END = 'terminate_on_end'
    C_TERMINATE_WHEN_FETCHED = 'terminate_when_fetched'

    CONFIG_DEFAULTS = {
        C_UPDATE_INTERVAL_S: 60*15,     # 15 minutes :)
        C_GRAPH_WORKER_ID: 'UNDEFINED',
        C_SOURCES_ENQUEUE_PORTION: 10,
        C_SOURCES_ENQUEUE_MAX: float('inf'),
        C_NEWS_FETCH_MAX: float('inf'),
        C_NEWS_FETCH_PER_SOURCE_MAX: float('inf'),
        C_MASTER_SLEEP_S: 10,
        C_SLAVE_SLEEP_S: 10,
        C_DO_NOT_FETCH: 0,
        C_TERMINATE_ON_END: 0,
        C_TERMINATE_WHEN_FETCHED: 0,
    }

    SUPPORTED_CONTENT_TYPES = ['text/plain', 'text/html']

    def __init__(
            self,
            master=False,
            config_file_name='',
            runtime_id=str(uuid.uuid1())[:8],
            master_sources_urls_file='',
            export_stats_to=None,
            export_cs_to=None,
            no_corleone=False,
            rabbit_mq_port=None,
            rabbit_mq_host=None,
            rabbit_mq_queue=None
    ):
        """
        @param rabbit_mq_queue: Target queue where will be exported news as jsons
        @param master: master Spidercrab object
        @type master: Spidercrab
        """

        
        try:
            stats = json.loads(open(self.STANDARD_STATS_EXPORT_FILE, "r").read())
        except:
            # Clean logs. TODO: do not use unix command
            os.system("rm "+self.STANDARD_STATS_EXPORT_FILE)

        self.logger = logger
        # Config used to be stored inside the database (only values from file)
        self.given_config = dict()
        # Config that will be used in computing (supplemented with defaults)
        self.config = dict()
        self._init_config(master, config_file_name)

        self.required_privileges = construct_full_privilege()
        # TODO: use configuration!
        self.odm_client = Client('localhost', 7777)
        self.terminate_event = threading.Event()
        self.runtime_id = runtime_id
        self.master_sources_urls_file = master_sources_urls_file
        self.export_stats_to = export_stats_to
        self.export_cs_to = export_cs_to
        self.no_corleone = no_corleone

        self.master = master
        if master:
            self.is_master = True
            self.level = 'master'
            if self.master_sources_urls_file:
                self.content_sources_urls = self._read_file(
                    self.master_sources_urls_file
                )
        else:
            self.is_master = False
            self.level = 'slave'

        self.fullname = '[' + self.config[self.C_GRAPH_WORKER_ID] + ' ' + \
            self.level + ' ' + self.runtime_id + ']'

        self.stats = dict()
        self._init_stats()

        self._sources_stack = list()

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
        params['master'] = True
        spidercrab_master = Spidercrab(**params)
        logger.log(info_level, '... Created Spidercrab master.')
        return spidercrab_master

    @staticmethod
    def create_worker(**params):
        """
            @param **params - parameters passed to the constructor
            @returns GraphWorker object
        """
        logger.log(info_level, 'Creating Spidercrab worker...')
        spidercrab_worker = Spidercrab(**params)
        logger.log(info_level, '... Created Spidercrab worker.')
        return spidercrab_worker

    def run(self):
        """
            Parameter-less run of GraphWorker object.
            You should run any Spidercrab (master and slave) with this method.
        """
        self._init_run()

        if self.is_master:
            queued_sources = 0
            while queued_sources < self.config[self.C_SOURCES_ENQUEUE_MAX]:
                if self.master_sources_urls_file:
                    # Enqueue from file new sources to be browsed by slaves
                    self._enqueue_source_lines()
                    if self.config[self.C_TERMINATE_ON_END]:
                        break
                else:
                    # Enqueue existing sources to be browsed by workers
                    result = self._enqueue_sources_portion()
                    queued_sources += len(result)
                    if len(result) == 0:
                        if self.config[self.C_TERMINATE_ON_END]:
                            break
                        else:
                            time.sleep(self.config[self.C_MASTER_SLEEP_S])
                    if self.terminate_event.is_set():
                        break

        else:  # slave case
            time_left = self.config[self.C_SLAVE_SLEEP_S]
            while not self.terminate_event.is_set():
                source = self._pick_pending_source()
                if not source:
                    # Maybe master is adding something right now? - wait.
                    time.sleep(1)
                    time_left -= 1
                    if time_left < 0:
                        self.logger.log(
                            info_level, self.fullname + ' No more tasks.')
                        if self.config[self.C_TERMINATE_ON_END]:
                            break
                        else:
                            time.sleep(self.config[self.C_SLAVE_SLEEP_S])
                else:
                    time_left = self.config[self.C_SLAVE_SLEEP_S]
                    source_props = self._update_source(source)
                    if self.config[self.C_DO_NOT_FETCH]:
                        continue
                    if 'news' in source_props:
                        fetched_news = self.stats[self.S_FETCHED_NEWS]
                        fetch_max = self.config[self.C_NEWS_FETCH_MAX]
                        if fetched_news < fetch_max:
                            self._fetch_new_news(source_props)
                        elif self.config[self.C_TERMINATE_WHEN_FETCHED]:
                            break
                        self.logger.log(
                            info_level,
                            self.fullname + ' Stats: ' + str(self.stats)
                        )
                    else:
                        self.logger.log(
                            error_level,
                            self.fullname + ' No news for ' + source['link']
                            + ' ... Parsed source properties: '
                            + str(source_props))

        self._end_run()

    def get_stats(self):
        return self.stats

    def stub_for_mantis_kafka_push(self, node_dictionary):
        print node_dictionary

    def _init_run(self):
        self.odm_client.connect()

        logger.log(info_level, self.fullname + ' Started.')

        if not self.is_master:
            if not self.no_corleone:
                self._check_and_pull_config()
            return

        # Check database structure and init if needed
        self._check_and_init_db()

        # Register our spidercrab instance in db if not registered
        self._check_and_register()

    def _end_run(self):
        self.odm_client.disconnect()
        logger.log(
            info_level,
            self.fullname + ' Finished!\nStats:\n' + str(self.stats))
        self._export_stats_to(self.STANDARD_STATS_EXPORT_FILE)
        if not self.export_stats_to is None and self.export_stats_to != self.STANDARD_STATS_EXPORT_FILE:
            self._export_stats_to(self.export_stats_to)

    def _export_stats_to(self, file_name):
        json_export = {
            'timestamp': time.time(),
            'runtime_id': self.runtime_id,
            'stats': self.stats
        }
        data = None
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as json_file:
                json_file.write(json.dumps({}))
        try:
            with open(file_name, 'r') as json_file: 
                x= json_file.read()
                data = json.loads(x)
            try:
                graph_worker_id = self.config[self.C_GRAPH_WORKER_ID]
                if graph_worker_id not in data:
                    data[graph_worker_id] = dict()
                if self.level not in data[graph_worker_id]:
                    data[graph_worker_id][self.level] = []
                data[graph_worker_id][self.level].append(json_export)
            finally:
                with open(file_name, 'w') as json_file:
                    json_file.write(json.dumps(data))
        except IOError as e:
            print e
            pass
        return True

    def _check_and_pull_config(self):
        """
            If there is a registered master Spidercrab in the database,
            fetches its config and merges with config used by this worker
            (not a config file). This method is used by slave workers.
        """
        if not self._is_master_registered():
            raise KeyError(
                'There is no registered Spidercrab master with '
                'graph_worker_id = \''
                + str(self.given_config['graph_worker_id']) + '\'!')

        master_config = du.get_running_service(
            service_params={
                'graph_worker_id': self.given_config['graph_worker_id']
            },
            enforce_running=False
        )['service_config']
        if master_config is None:
            self.logger.log(
                error_level,
                self.fullname + ' Error Corleone get_running_service().'
            )
        for param in master_config.keys():
            self.config[param] = master_config[param]
        self.logger.log(
            info_level, self.fullname + ' Pulled config from master.'
        )

    def _is_master_registered(self):
        response = self.odm_client.get_instances('Spidercrab')
        master_node = {}
        for instance in response:
            if instance['graph_worker_id'] == \
                    self.given_config['graph_worker_id']:
                master_node = instance
        if len(master_node) == 0:
            return False
        return True

    def _check_and_init_db(self):
        """
            Checks if Spidercrab meta-nodes are present in the database.
            If not - initializes them.
        """
        # Check if our model is present
        response = self.odm_client.get_model_nodes()
        models = []
        logger.info("Response get_model_nodes(): "+str(response))
        for model in response:
            # NOTE: Workaround - no 'model_name' property in Model node...
            if 'model_name' in model:
                models.append(model['model_name'])
            else:
                self.logger.error("No model_name in model pulled \
                    from neo4j!")
        if not 'Spidercrab' in models:
            self.logger.log(
                info_level,
                'Spidercrab model not found in the database. Creating...'
            )
            self.odm_client.create_model_node('Spidercrab')
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
        instances = self.odm_client.get_instances('Spidercrab')
        master_uuid = ''
        graph_worker_id = self.config[self.C_GRAPH_WORKER_ID]

        for instance in instances:
            if instance['graph_worker_id'] == graph_worker_id:
                master_uuid = instance['uuid']
        if master_uuid:
            self.logger.log(
                info_level,
                'Spidercrab ' + graph_worker_id
                + ' already registered in the database. '
                + ' Updating config...'
            )
            params = self.given_config
            self.odm_client.set(master_uuid, **params)
        else:
            self.logger.log(
                info_level,
                'Registering ' + graph_worker_id
                + ' Spidercrab in the database.'
            )
            params = self.given_config
            self.odm_client.create_node(
                model_name='Spidercrab',
                rel_type=HAS_INSTANCE_RELATION,
                **params
            )

    def _init_config(self, master, config_file_name='',):
        """
            Checks if there config file exists and initializes it if needed.
        """
        service_name = 'spidercrab_slave'
        if master:
            service_name = 'spidercrab_master'
        if config_file_name == '':
            # No config file - load from Don Corleone
            don_config = du.get_running_service(
                service_name=service_name,
                node_id=du.get_my_node_id(),
                enforce_running=False
            )['service_config']

            for param in self.CONFIG_DEFAULTS.keys():
                try:
                    self.given_config[param] = don_config[param]
                    self.config[param] = self.given_config[param]
                except Exception as error:
                    self.logger.log(
                        error_level, 'Don Corleone: ' + str(error)
                    )
                    self.config[param] = self.CONFIG_DEFAULTS[param]
            if not self.given_config.get('graph_worker_id'):
                # Bad or no config in Don Corleone
                raise KeyError(
                    'Please set up your Spidercrab config inside Don '
                    'Corleone config.json or use your own spidercrab.json '
                    'separate config file! (Check if you have set the '
                    '"graph_worker_id" property)'
                )
        else:
            if not os.path.isfile(config_file_name):
                shutil.copy(self.TEMPLATE_CONFIG_NAME, config_file_name)
                raise ValueError(
                    'Please set up your config file created under '
                    + config_file_name + '!'
                )

            # Load user defined config file
            self.given_config = dict(json.load(open(config_file_name)))
            self.config = dict(json.load(open(config_file_name)))

        # Create a final dictionary with default values
        for param in self.CONFIG_DEFAULTS.keys():
            if param not in self.config:
                self.config[param] = self.CONFIG_DEFAULTS[param]

        if self.config[self.C_GRAPH_WORKER_ID] == 'UNDEFINED':
            raise ValueError(
                'Please choose your id and enter it inside '
                + config_file_name + '!'
            )

    def _init_stats(self):
        if self.is_master:
            self.stats = {
                'total_queued_sources': 0,
            }
        else:
            self.stats = {
                'total_fetched_news': 0,
                'total_extracted_news': 0,
                'total_updated_sources': 0,
            }

    @staticmethod
    def _read_file(file_name):
        """
            Read lines of file and return them as list.
        """
        lines = []
        try:
            f = open(file_name, 'r')
            try:
                lines = f.readlines()
            finally:
                f.close()
        except IOError as e:
            print e
            exit()
        return lines

    def _enqueue_source_lines(self):
        """
            Read one line of content source url from master_sources_urls_file,
            insert it into the database and assign it 'pending' relation
            with own Spidercrab node.

            Method used by master.
        """
        count = len(self.content_sources_urls)
        n = 0
        for line in self.content_sources_urls:
            n += 1
            if n > self.config[self.C_SOURCES_ENQUEUE_MAX]:
                break
            self.logger.log(
                info_level,
                self.fullname + ' Adding (' + str(n) + '/' + str(count) + ') '
                + line[:-1] + ' ...'
            )
            # Check if not in database
            query = """
            MATCH
                (source:ContentSource {link: '%s'}),
                (crab:Spidercrab {graph_worker_id: '%s'})
            CREATE UNIQUE (crab)-[:pending]->(source)
            RETURN source
            """
            query %= (
                line[:-1],
                self.config[self.C_GRAPH_WORKER_ID]
            )
            result = self.odm_client.execute_query(query)
            if result:
                self.logger.log(
                    info_level,
                    self.fullname + ' Source ' + line[:-1]
                    + ' already present - queuing if not queued.'
                )
                continue
            try:
                # Try adding url from this line
                params = {
                    'source_type': 'unknown',
                    'link': line[:-1],
                }
                self.odm_client.create_node(
                    CONTENT_SOURCE_TYPE_MODEL_NAME,
                    HAS_INSTANCE_RELATION,
                    **params
                )
                # Create a `pending` relation
                query = """
                MATCH
                    (source:ContentSource {link: '%s'}),
                    (crab:Spidercrab {graph_worker_id: '%s'})
                CREATE UNIQUE (crab)-[:pending]->(source)
                RETURN source
                """
                query %= (
                    line[:-1],
                    self.config[self.C_GRAPH_WORKER_ID]
                )
                result = self.odm_client.execute_query(query)
                self.stats[self.S_QUEUED_SOURCES] += len(result)
            except Exception as error:
                self.logger.log(
                    error_level,
                    self.fullname + ' Error occurred with adding `'
                    + line[:-1] + '`:\n' + str(error) + '\nContinuing...\n'
                )

    def _enqueue_sources_portion(self):
        """
            Fetch portion of sources defined in config and immediately assign
            them 'pending' relation with own Spidercrab node.

            Method used by master.
        """
        query = """
        MATCH
            (source:ContentSource),
            (crab:Spidercrab {graph_worker_id: '%s'})
        WHERE %s - source.last_updated > %s
            AND NOT (crab)-[:pending]->(source)
        CREATE (crab)-[:pending]->(source)
        RETURN source
        LIMIT %s
        """
        query %= (
            self.config[self.C_GRAPH_WORKER_ID],
            database_gmt_now(),
            self.config[self.C_UPDATE_INTERVAL_S],
            self.config[self.C_SOURCES_ENQUEUE_PORTION],
        )
        result = self.odm_client.execute_query(query)
        self.logger.log(
            info_level,
            self.fullname + ' Master queued ' + str(len(result)) + ' sources.'
        )
        self.stats[self.S_QUEUED_SOURCES] += len(result)
        return result

    def _pick_pending_source(self):
        """
            Pick first free ContentSource (pending in master Spidercrab node),
            remove pending rel and mark it as updated. Method used by workers.
        """
        query = """
        MATCH
            (crab:Spidercrab {graph_worker_id: '%s'})
            -[r:pending]->
            (source:ContentSource)
        SET source.last_updated = %s
        DELETE r
        RETURN source
        LIMIT 1
        """
        query %= (
            self.config[self.C_GRAPH_WORKER_ID],
            database_gmt_now(),
        )
        result = self.odm_client.execute_query(query)
        if len(result) > 0:
            self.logger.log(
                info_level,
                self.fullname + ' Picked ' + str(result[0][0]['link'])
            )
            return result[0][0]
        else:
            return None

    def _update_source(self, source_node):
        """
            Update params of given node (a dict with 'uuid' and 'link' keys)
            and return its properties.
        """
        properties = dict()
        source_link = source_node['link']
        self._sources_stack = [source_link]
        try:
            properties = self._parse_source(source_link)
        except Exception as error:
            self.logger.log(
                error_level,
                self.fullname + ' ' + source_link
                + ' - Parsing error: ' + str(error)
            )

        if self.export_cs_to and len(properties) > 1:
            self._export_cs(properties)

        if 'link' not in properties:
            self.logger.log(
                info_level,
                self.fullname + ' There is no valid feed url for wrong url '
                + source_link + ' - aborting update...'
            )
            return properties

        if properties['link'] != source_link:
            self.logger.log(
                info_level,
                self.fullname + ' url ' + source_link + ' changed to '
                + properties['link'] + ' ... (web page forwarding/transfer?)'
                + ' Checking if this source already exists...'
            )
            destination_node = self.odm_client.get_by_link(
                CONTENT_SOURCE_TYPE_MODEL_NAME,
                properties['link']
            )
            if destination_node:
                self.logger.log(
                    info_level,
                    self.fullname + ' This source already exists - '
                    'Leaving it.'
                )
                # This approach gives an opportunity to avoid deadlock
                # and in fact does not leave existing source if queued
                # - this source will be updated by this or another slave later
                return properties
                #source_node['uuid'] = destination_node['uuid']

        query = """
        MATCH (source:ContentSource {uuid: '%s'})
        SET
            source.language = '%s',
            source.title = '%s',
            source.link = '%s',
            source.description = '%s',
            source.source_type = '%s'
        RETURN source
        """
        query %= (
            source_node['uuid'],
            properties.get('language', 'unknown'),
            properties.get('title', 'unknown'),
            properties.get('link', 'unknown'),
            properties.get('description', 'unknown'),
            properties.get('source_type', 'unknown')
        )
        self.logger.log(
            info_level,
            self.fullname
            + ' Updating ContentSource of ' + properties['link']
        )
        result = self.odm_client.execute_query(query)
        self.stats[self.S_UPDATED_SOURCES] += len(result)

        # Optional ContentSource properties
        if 'image' in properties:
            query = """
            MATCH (source:ContentSource {uuid: '%s'})
            SET
                source.image_url = '%s',
                source.image_width = '%s',
                source.image_height = '%s',
                source.image_link = '%s'
            RETURN source
            """
            query %= (
                source_node['uuid'],
                properties.get('image_url'),
                properties.get('image_width'),
                properties.get('image_height'),
                properties.get('image_link'),
            )
            self.odm_client.execute_query(query)
        properties['uuid'] = source_node['uuid']
        return properties

    def _parse_source(self, source_link):
        """
            Parse source properties to a dictionary using various methods.
            (For later use with methods for other further content sources)
        """
        # Default values
        properties = {
            'description': 'unknown',
            'language': 'unknown',
            'link': source_link,
            'source_type': 'unknown',
            'title': 'unknown'
        }
        data = feedparser.parse(source_link)

        if not Spidercrab._source_has_entries(data):
            logger.log(
                error_level,
                data.get('href', '(Unknown url)') + ' is not a feed!')
            another_props = self._try_another_source_link(data)
            if not another_props:
                return properties
            else:
                return another_props

        version = data.get('version', 'unknown')
        if version[:3] == 'rss' or version == 'unknown' or not version:
            parsed_properties = self._parse_rss_source(data)
            properties.update(parsed_properties)
        return properties

    @staticmethod
    def _source_has_entries(data):
        """
            Check if there are entries in this source data dictionary.
        """
        return len(data.get('entries', [])) != 0

    def _parse_rss_source(self, data):
        properties = dict()
        try:
            # Common RSS elements
            feed = data['feed']
            properties['description'] = feed.get('description', 'unknown')
            properties['language'] = feed.get('language', 'unknown')
            properties['source_type'] = 'rss'
            properties['title'] = feed.get('title', 'unknown')
            properties['link'] = data.get('href', 'unknown')
            # Optional ContentSource properties
            if 'image' in feed and 'href' in feed['image']:
                image = feed['image']
                if 'href' in image:
                    properties['image_url'] = image['href']
                if 'width' in image:
                    properties['image_width'] = image['width']
                if 'height' in image:
                    properties['image_height'] = image['height']
                if 'link' in image:
                    properties['image_link'] = image['link']
            # News
            properties['news'] = []
            for entry in data['entries']:
                news = dict()
                news['title'] = unicode(entry.get('title', 'unknown'))
                news['summary'] = entry.get('summary', 'unknown')
                news['link'] = unicode(entry.get('link', 'unknown'))
                news['published'] = unicode(
                    time_struct_to_database_timestamp(
                        entry.get('published_parsed', 'unknown'))
                )
                properties['news'].append(news)
        except Exception as error:
            logger.log(error_level, 'RSS XML error - ' + str(error))
        return properties

    def _db_encode(self, string, encoding='unknown'):
        """
            Encode string so that it can be safely put inside the database
        """
        return unicode(string).replace('\'', '\\\'')

    def _try_another_source_link(self, data):
        feed = data['feed']
        properties = dict()
        try:
            for link in feed.get('links', []):
                if link.get('href') in self._sources_stack:
                    continue
                # TODO: Other feeds
                if 'rss' in link.get('type', ''):
                    logger.log(
                        info_level, 'Trying ' + str(link.get('href')) + ' ...'
                    )
                    properties = self._parse_source(link['href'])
        except Exception as error:
            logger.log(error_level, 'RSS XML error - ' + str(error))
        return properties

    def _fetch_new_news(self, source_props):
        """
            Fetches news text and HTML from news_list visiting and extracting
            website.
        """
        news_list = source_props['news']
        fetch_max = self.config[self.C_NEWS_FETCH_MAX]
        fetch_max_ps = self.config[self.C_NEWS_FETCH_PER_SOURCE_MAX]
        fetched_news_ps = 0

        for news_props in news_list:
            if fetched_news_ps >= fetch_max_ps:
                logger.log(
                    info_level,
                    self.fullname + ' fetched ' + str(fetched_news_ps)
                    + ' news - nothing to do here!'
                )
                break
            fetched_news = self.stats[self.S_FETCHED_NEWS]
            if fetched_news >= fetch_max:
                logger.log(
                    info_level,
                    self.fullname + ' fetched total of ' + str(fetched_news)
                    + ' news from all sources - nothing to do here!'
                )
                break

            # Check if this news is already present in the database
            query = """
                MATCH
                (source:ContentSource {uuid: '%s'})
                -[:`%s`]->
                (news:Content {link: '%s'})
                RETURN news
                """
            query %= (
                source_props['uuid'],
                PRODUCES_RELATION,
                news_props['link'],
            )
            result = self.odm_client.execute_query(query)

            if not result:

                try:
                    news_props = self._extract_news(news_props)
                except Exception as error:
                    self.logger.log(
                        error_level,
                        self.fullname + ' ' + news_props['link']
                        + ' - Extracting error: ' + unicode(error)
                    )
                # Prepare strings to database
                for key in news_props:
                    news_props[key] = self._db_encode(news_props[key])
                query = u"""
                    MATCH
                    (source:ContentSource {uuid: '%s'}),
                    (cs_model:Model {model_name: 'Content'})
                    CREATE UNIQUE
                    (source)
                    -[:`%s`]->
                    (news:Content:NotYetTagged {
                        uuid: '%s',
                        title: '%s',
                        summary: '%s',
                        link: '%s',
                        published: %s,
                        text: '%s',
                        html: '%s',
                        type: '%s'
                    }),
                    (cs_model)
                    -[:`%s`]->
                    (news)
                    RETURN news
                    """
                query %= (
                    source_props['uuid'],
                    PRODUCES_RELATION,
                    uuid.uuid1(),
                    news_props.get('title', 'unknown'),
                    news_props.get('summary', 'unknown'),
                    news_props.get('link', 'unknown'),
                    news_props.get('published', 'unknown'),
                    news_props.get('text', 'unknown'),
                    'TODO',  # news_props['html'],
                    news_props.get('type', 'unknown'),
                    HAS_INSTANCE_RELATION
                )
                result = self.odm_client.execute_query(query)
                if result:
                    self.stub_for_mantis_kafka_push(result[0][0])
                fetched_news_ps += len(result)
                self.stats[self.S_FETCHED_NEWS] += len(result)
                if not result:
                    self.logger.log(
                        error_level,
                        self.fullname + ' Not added ' + news_props['link']
                        + ' !!! - check Lionfish logs!'
                    )
            if fetched_news_ps > 0:
                self.logger.log(
                    info_level,
                    self.fullname + ' Fetched ' + str(fetched_news_ps)
                    + '. news for ' + source_props['link'])

    def _inspect_news(self, url):
        """
            Inspect meta properties of the page.
        """
        result = dict()
        news = urllib2.urlopen(url)
        result['content_type'] = news.headers.get('content-type', 'unknown')
        return result

    def _content_is_supported(self, content_type, url='unknown'):
        """
            Exclude media files etc. from extraction.
        """
        for supported in self.SUPPORTED_CONTENT_TYPES:
            if supported in content_type:
                return True

        self.logger.log(
            info_level,
            self.fullname + ' ' + str(url)
            + ' - This content is not supported in extraction! '
            + '(' + str(content_type) + ')'
        )
        return False

    def _extract_news(self, news_props):
        """
            Extracts content of news.
            TODO: Fix encoding
        """
        news_props['text'] = 'unknown'
        news_props['html'] = 'unknown'

        meta_props = self._inspect_news(news_props['link'])
        for key in meta_props:
            news_props[key] = meta_props[key]

        if not self._content_is_supported(
                news_props['content_type'],
                news_props['link']
        ):
            return news_props

        self.logger.log(
            info_level,
            self.fullname + ' extracting ' + str(news_props['link'])
        )

        try:
            extractor = boilerpipe.extract.Extractor(
                extractor='ArticleExtractor', url=news_props['link']
            )
            news_props['text'] = unicode(extractor.getText())
            news_props['html'] = unicode(extractor.getHTML())
            self.stats[self.S_EXTRACTED_NEWS] += 1
        except Exception as error:
            logger.log(error_level, error)
        #TODO: news images
        # bs_html = BeautifulSoup(urllib2.urlopen(news_link))
        #news_props['images'] = []
        return news_props

    @staticmethod
    def _export_line(line, file_name):
        """ Export line to file """
        try:
            f = open(file_name, 'a')
            try:
                f.write(line + '\n')
            finally:
                f.close()
        except IOError as e:
            print e
            pass
        return True

    def _export_cs(self, properties):
        exported = {
            'source_type': properties['source_type'],
            'link': properties['link'],
            'description': properties['description'],
            'title': properties['title'],
            'language': properties['language']
        }
        Spidercrab._export_line(str(exported), self.export_cs_to)


if __name__ == '__main__':
    print "Please run spidercrab_master.py or spidercrab_slave.py in order " \
          "to run a proper graph worker(s)."
    print "Press Enter to create one master with 5 slaves."
    enter = raw_input()

    master_sc = Spidercrab.create_master()
    thread = threading.Thread(target=master_sc.run)
    thread.start()

    time.sleep(3)
    for i in range(5):
        worker = Spidercrab.create_worker(runtime_id=str(i))
        thread = threading.Thread(target=worker.run)
        thread.start()
