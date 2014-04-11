"""
    Spidercrab - simple, synchronized news fetching GraphWorker
"""

#from BeautifulSoup import BeautifulSoup
import boilerpipe.extract
import feedparser
import os
import shutil
import sys
import threading
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))
from don_utils import get_configuration

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

    TEMPLATE_CONFIG_NAME = './spidercrab.json.template'
    CONFIG_DEFAULTS = {
        'update_interval_s': 60*15,     # 15 minutes :)
        'graph_worker_id': 'UNDEFINED',
        'sources_enqueue_portion': 10,
        'sources_enqueue_max': float('inf'),
        'worker_sleep_s': 10,
        'do_not_fetch': 0,
    }

    def __init__(
            self,
            master=False,
            config_file_name='',
            runtime_id=str(uuid.uuid1())[:8],
            master_sources_urls_file='',
            export_cs_to=None,
    ):
        """
        @param master: master Spidercrab object
        @type master: Spidercrab
        """
        self.logger = logger
        # Config used to be stored inside the database (only values from file)
        self.given_config = {}
        # Config that will be used in computing (supplemented with defaults)
        self.config = {}
        self._init_config(master, config_file_name)

        self.required_privileges = construct_full_privilege()
        self.odm_client = ODMClient()
        self.terminate_event = threading.Event()
        self.runtime_id = runtime_id
        self.master_sources_urls_file = master_sources_urls_file
        self.export_cs_to = export_cs_to

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

        self.fullname = '[' + self.config['graph_worker_id'] + ' ' + \
            self.level + ' ' + self.runtime_id + ']'

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
                if self.master_sources_urls_file:
                    # Enqueue from file new sources to be browsed by slaves
                    self._enqueue_source_lines()
                    break
                else:
                    # Enqueue existing sources to be browsed by workers
                    result = self._enqueue_sources_portion()
                    queued_sources += len(result)
                    if len(result) == 0 or self.terminate_event.is_set():
                        break

        else:  # slave case
            time_left = WORKER_SLEEP_S
            while not self.terminate_event.is_set():
                source = self._pick_pending_source()
                if not source:
                    # Maybe master is adding something right now? - wait.
                    time.sleep(1)
                    time_left -= 1
                    if time_left < 0:
                        self.logger.log(
                            info_level, self.fullname + ' No more tasks.')
                        break
                else:
                    time_left = WORKER_SLEEP_S
                    source_props = self._update_source(source)
                    if self.config['do_not_fetch']:
                        continue
                    if 'news' in source_props:
                        self._fetch_new_news(
                            source['uuid'], source_props['news'])
                    else:
                        self.logger.log(
                            error_level,
                            'No news for ' + source['link'] + ' ... '
                            + 'Parsed source properties: '
                            + str(source_props))

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
            if instance['graph_worker_id'] == \
                    self.given_config['graph_worker_id']:
                master_node = instance
        if len(master_node) == 0:
            raise KeyError(
                'There is no registered Spidercrab master with '
                'graph_worker_id = \''
                + str(self.given_config['graph_worker_id']) + '\'!')
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
        instances = self.odm_client.get_instances('Spidercrab')
        master_uuid = ''
        for instance in instances:
            if instance['graph_worker_id'] == self.config['graph_worker_id']:
                master_uuid = instance['uuid']
        if master_uuid:
            # TODO: OVERWRITE the whole config in database (Lionfish update)
            self.logger.log(
                info_level,
                'Spidercrab ' + self.config['graph_worker_id']
                + ' already registered in the database. '
                + ' Updating config...'
            )
            params = self.given_config
            self.odm_client.set(master_uuid, **params)
        else:
            self.logger.log(
                info_level,
                'Registering ' + self.config['graph_worker_id']
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
            for param in self.CONFIG_DEFAULTS.keys():
                try:
                    self.given_config[param] = get_configuration(
                        service_name, param)
                    self.config[param] = self.given_config[param]
                except Exception as error:
                    self.logger.log(
                        error_level, 'Don Corleone error: ' + str(error)
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

        if self.config['graph_worker_id'] == 'UNDEFINED':
            raise ValueError(
                'Please choose your id and enter it inside '
                + config_file_name + '!'
            )

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
            if n > self.config['sources_enqueue_max']:
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
                self.config['graph_worker_id']
            )
            result = self.odm_client.execute_query(query)
            if result:
                self.logger.log(
                    info_level,
                    self.fullname + ' Source ' + line[:-1]
                    + ' already present - queuing.'
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
                    self.config['graph_worker_id']
                )
                self.odm_client.execute_query(query)
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
            self.config['graph_worker_id'],
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
            (crab:Spidercrab {graph_worker_id: '%s'})
            -[r:pending]->
            (source:ContentSource)
        SET source.last_updated = %s
        DELETE r
        RETURN source
        LIMIT 1
        """
        query %= (
            self.config['graph_worker_id'],
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

        if self.export_cs_to and len(properties) > 1:
            self._export_cs(properties)

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
            properties.get('title', 'unknown'),
            properties.get('description', 'unknown'),
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
        # Default values
        properties = {
            'description': 'unknown',
            'language': 'unknown',
            'link': source_link,
            'source_type': 'unknown',
            'title': 'unknown'
        }
        data = feedparser.parse(source_link)

        version = data.get('version', 'unknown')
        if version[:3] == 'rss' or version == 'unknown':
            parsed_properties = Spidercrab._parse_rss_source(data)
            properties.update(parsed_properties)
        return properties

    @staticmethod
    def _parse_rss_source(data):
        properties = dict()
        try:
            # Common RSS elements
            feed = data['feed']
            properties['description'] = feed.get('description', 'unknown')
            properties['language'] = feed.get('language', 'unknown')
            properties['source_type'] = 'rss'
            properties['title'] = feed.get('title', 'unknown')
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
                news['summary'] = unicode(entry.get('summary', 'unknown'))
                news['link'] = unicode(entry.get('link', 'unknown'))
                news['published'] = unicode(
                    time_struct_to_database_timestamp(
                        entry.get('published_parsed', 'unknown'))
                )
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
                    (news:Content:NotYetTagged {
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
        news_props['text'] = 'unknown'
        news_props['html'] = 'unknown'
        try:
            extractor = boilerpipe.extract.Extractor(
                extractor='ArticleExtractor', url=news_props['link']
            )
            news_props['text'] = unicode(extractor.getText())
            news_props['html'] = unicode(extractor.getHTML())
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