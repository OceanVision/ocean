"""
    Spidercrab - simple, synchronized news fetching GraphWorker
"""

#from BeautifulSoup import BeautifulSoup
import boilerpipe.extract
import feedparser
import shutil
import threading
import uuid

from graph_workers.graph_defines import *
from graph_workers.graph_utils import *
from graph_workers.graph_worker import GraphWorker
from graph_workers.privileges import construct_full_privilege
from odm_client import ODMClient

SOURCES_ENQUEUE_PORTION = 10
SOURCES_ENQUEUE_MAX = float('inf')
WORKER_SLEEP_S = 10

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

    DEFAULT_CONFIG_NAME = './spidercrab.json.default'
    CONFIG_FILE_NAME = './spidercrab.json'
    CONFIG_DEFAULTS = {
        'update_interval_s': 1000*60*15,     # 15 minutes :)
        'use_all_sources': True,
        'content_sources': [],
        'worker_id': 'undefined',
        'sources_enqueue_portion': 10,
        'sources_enqueue_max': float('inf'),
        'worker_sleep_s': 10,
    }

    def __init__(
            self,
            master=False,
            config_file_name=CONFIG_FILE_NAME,
            runtime_id=str(uuid.uuid1())[:8],
    ):
        """
        @param master: master Spidercrab object
        @type master: Spidercrab
        """
        # Config used to be stored inside the database (only values from file)
        self.given_config = {}
        # Config that will be used in computing (supplemented with defaults)
        self.config = {}
        self._init_config(config_file_name)

        self.logger = logger
        self.required_privileges = construct_full_privilege()
        self.odm_client = ODMClient()
        self.terminate_event = threading.Event()
        self.runtime_id = runtime_id

        self.master = master
        if master:
            self.is_master = True
            self.level = 'master'
        else:
            self.is_master = False
            self.level = 'slave'

        self.fullname = '[' + self.config['worker_id'] + ' ' + self.level + \
            ' ' + self.runtime_id + ']'

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
            while queued_sources < self.config['sources_enqueue_max']:
                # Enqueue new sources to be browsed by workers
                result = self._enqueue_sources_portion()
                queued_sources += len(result)
                if len(result) == 0 or self.terminate_event.is_set():
                    break

        else:  # worker case
            time_left = WORKER_SLEEP_S
            while not self.terminate_event.is_set():
                source = self._pick_pending_source()
                if not source:
                    # Maybe master is adding something right now? - wait.
                    time.sleep(1)
                    time_left -= 1
                    if time_left < 0:
                        self.logger.log(
                            info_level,
                            self.fullname + ' No more pending tasks.'
                        )
                        break
                else:
                    time_left = WORKER_SLEEP_S
                    news_list = self._update_source(source)['news']
                    self._fetch_new_news(source['uuid'], news_list)

        self._end_run()

    def _init_run(self):
        self.odm_client.connect()

        logger.log(info_level, self.fullname + ' Started.')

        if not self.is_master:
            self._check_and_pull_config()
            return

        # Check database structure and init if needed
        self._check_and_init_db()

        # Register our spidercrab instance in db if not registered
        self._check_and_register()

    def _end_run(self):
        self.odm_client.disconnect()
        logger.log(info_level, self.fullname + ' Finished!')

    def _check_and_pull_config(self):
        """
            If there is a registered master Spidercrab in the database,
            fetches its config and merges with config used by this worker
            (not a config file). This method is used by slave workers.
        """
        response = self.odm_client.get_instances('Spidercrab')
        master_node = {}
        for instance in response:
            if instance['worker_id'] == self.given_config['worker_id']:
                master_node = instance
        if len(master_node) == 0:
            raise KeyError(
                'There is no registered Spidercrab master with worker_id = '
                + str(self.given_config['worker_id']) + '!')
        master_node.pop('uuid')
        for param in master_node.keys():
            self.config[param] = master_node[param]
        self.logger.log(
            info_level, self.fullname + ' Pulled config from master.'
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
            params = self.given_config
            self.odm_client.create_node(
                model_name='Spidercrab',
                rel_type=HAS_INSTANCE_RELATION,
                **params
            )

    def _init_config(self, config_file_name=CONFIG_FILE_NAME):
        """
            Checks if there config file exists and initializes it if needed.
        """
        if not os.path.isfile(config_file_name):
            shutil.copy(self.DEFAULT_CONFIG_NAME, config_file_name)
            raise ValueError(
                'Please set up your config file created under '
                + config_file_name + '!'
            )
        self.given_config = dict(json.load(open(config_file_name)))

        self.config = dict(json.load(open(config_file_name)))
        for param in self.CONFIG_DEFAULTS.keys():
            if param not in self.config:
                self.config[param] = self.CONFIG_DEFAULTS[param]

        if self.config['worker_id'] == 'UNDEFINED':
            raise ValueError(
                'Please choose your id and enter it inside '
                + config_file_name + '!'
            )

    def _enqueue_sources_portion(self):
        """
            Fetch portion of sources defined in config and immediately assign
            them 'pending' relation with own Spidercrab node. Method used by
            master.
        """
        query = """
        MATCH
            (source:ContentSource),
            (crab:Spidercrab {worker_id: '%s'})
        WHERE %s - source.last_updated > %s
            AND NOT crab-[:pending]->source
        CREATE (crab)-[:pending]->(source)
        RETURN source
        LIMIT %s
        """
        query %= (
            self.config['worker_id'],
            database_gmt_now(),
            self.config['update_interval_s'],
            self.config['sources_enqueue_portion'],
        )
        result = self.odm_client.execute_query(query)
        self.logger.log(
            info_level, 'Master queued ' + str(len(result)) + ' sources.'
        )
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
            (source:ContentSource)
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
        properties = self._parse_source(source_node['link'])
        query = """
        MATCH (source:ContentSource {uuid: '%s'})
        SET
            source.language = '%s',
            source.title = '%s',
            source.description = '%s',
            source.source_type = '%s'
        RETURN source
        """
        query %= (
            source_node['uuid'],
            properties.get('language', 'unknown'),
            properties.get('title', 'Untitled'),
            properties.get('description', 'No description'),
            properties.get('source_type', 'unknown')
        )
        self.logger.log(
            info_level,
            self.fullname
            + ' Updating ContentSource of ' + source_node['link']
        )
        self.odm_client.execute_query(query)

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
        return properties

    @staticmethod
    def _parse_source(source_link):
        """
            Parse source properties to a dictionary using various methods.
            (For later use with methods for other further content sources)
        """
        data = feedparser.parse(source_link)
        version = data['version']
        if version[:3] == 'rss':
            return Spidercrab._parse_rss_source(data)

    @staticmethod
    def _parse_rss_source(data):
        properties = dict()
        try:
            # Common RSS elements
            properties['language'] = data['feed']['language']
            properties['title'] = data['feed']['title']
            properties['description'] = data['feed']['description']
            properties['source_type'] = 'rss'
            # Optional ContentSource properties
            if 'image' in data['feed'] and 'href' in data['feed']['image']:
                properties['image_url'] = data['feed']['image']['href']
                properties['image_width'] = data['feed']['image']['width']
                properties['image_height'] = data['feed']['image']['height']
                properties['image_link'] = data['feed']['image']['link']
            # News
            properties['news'] = []
            for entry in data['entries']:
                news = dict()
                news['title'] = unicode(entry['title'])
                news['summary'] = unicode(entry['summary'])
                news['link'] = unicode(entry['link'])
                news['published'] = unicode(time_struct_to_database_timestamp(
                    entry['published_parsed']))
                properties['news'].append(news)
        except Exception as error:
            logger.log(error_level, 'RSS XML error - ' + str(error))
        return properties

    def _fetch_new_news(self, source_uuid, news_list):
        """
            Fetches news text and HTML from news_list visiting and extracting
            website.
        """
        for news_props in news_list:
            # Check if this news is already present in the database
            query = """
                MATCH
                (source:ContentSource {uuid: '%s'})
                -[:`%s`]->
                (news:Content {link: '%s'})
                RETURN news
                """
            query %= (
                source_uuid,
                PRODUCES_RELATION,
                news_props['link'],
            )
            result = self.odm_client.execute_query(query)

            if not result:
                self.logger.log(
                    info_level,
                    self.fullname + ' extracting ' + str(news_props['link'])
                )
                news_props = Spidercrab._extract_news(news_props)
                query = u"""
                    MATCH
                    (source:ContentSource {uuid: '%s'}),
                    (cs_model:Model {model_name: 'Content'})
                    CREATE UNIQUE
                    (source)
                    -[:`%s`]->
                    (news:Content {
                        title: '%s',
                        summary: '%s',
                        link: '%s',
                        published: %s,
                        text: '%s',
                        html: '%s'
                    }),
                    (cs_model)
                    -[:`%s`]->
                    (news)
                    RETURN news
                    """
                query %= (
                    source_uuid,
                    PRODUCES_RELATION,
                    news_props['title'],
                    news_props['summary'],
                    news_props['link'],
                    news_props['published'],
                    news_props['text'],
                    'TODO',  # news_props['html'],
                    HAS_INSTANCE_RELATION
                )
                self.odm_client.execute_query(query)

    @staticmethod
    def _extract_news(news_props):
        """
            Extracts content of news.
        """
        extractor = boilerpipe.extract.Extractor(
            extractor='ArticleExtractor', url=news_props['link']
        )
        news_props['text'] = unicode(extractor.getText())
        news_props['html'] = unicode(extractor.getHTML())
        #TODO: news images
        # bs_html = BeautifulSoup(urllib2.urlopen(news_link))
        #news_props['images'] = []
        return news_props


if __name__ == '__main__':
    print "Please run spidercrab_master.py or spidercrab_slaves.py in order " \
          "to run a proper graph worker(s)."
    spidercrab = Spidercrab.create_master()
    spidercrab.run()

    worker_1 = Spidercrab.create_worker()
    worker_2 = Spidercrab.create_worker()
    worker_3 = Spidercrab.create_worker()
    worker_1.run()
    worker_2.run()
    worker_3.run()