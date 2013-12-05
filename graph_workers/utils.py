""" Simple utility functions and objects """
import time
from pytz import timezone
import logging
import urlparse
import urllib2
import re
import random
import socket
import httplib
import xml.parsers.expat
import xml.dom.minidom
from datetime import timedelta, datetime
from dateutil import parser

MY_DEBUG_LEVEL = 25
MY_INFO_LEVEL = 35
MY_INFO_IMPORTANT_LEVEL = 32
MY_IMPORTANT_LEVEL = 40
MY_CRITICAL_LEVEL = 50

logging.basicConfig(level=MY_DEBUG_LEVEL)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False






# This regex tries to predict if there is a web page (refuses non-webpage links)
#TODO: Improve to reject images, download files etc.
HTTP_S_VALIDATION_REGEX = "^http[s]*\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$"

# This regex is used to search urls inside a webpage source code
HTTP_S_LINK_REGEX = "\"(http[s]*\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?)\""





def database_timestamp_to_datetime(timestamp):
	"""
		@param timestamp from database
		@returns datetime in GMT timezone
	"""

	dt = datetime.fromtimestamp(timestamp)
	dt = dt.replace(tzinfo=timezone("GMT")) # Otherwise it would do a conversion -1h  (if given timezone as parameter)
	return dt

def GMTdatetime_to_database_timestamp(dt):
	"""
		@param datetime in GMT timezone
		@returns timestamp in GMT timezone
	"""
	#TODO: add checking for GMT timezone.
	return int(time.mktime(dt.timetuple()))

def get_domain(url_string):
    """
        @returns domain of given url_string
    """
    return urlparse.urlsplit( url_string )[1].split(':')[0]


def get_domain_url(url_string):
    """
        @returns domain of given url_string with scheme prefix
    """
    url_split = urlparse.urlsplit( url_string )
    url_domain = url_split[0] + "://" + url_split[1]
    return url_domain


def unify_url(url_string):
    """
        @returns unified url, so that we can reduce the redundancy of visiting
            the same site specified by several urls
    """
    unified_url = url_string
    while unified_url[-1] == "/":
        unified_url = unified_url[:-1]
    return unified_url


def find_urls(string):
    """
        @returns a list of all (absolute) urls found inside a given string.
    """
    url_pairs = re.findall(HTTP_S_LINK_REGEX,string)
    urls = []
    for pair in url_pairs:
        urls.append(pair[0])
    return urls


def open_url(site_url):
    """
        @returns socket._fileobject contents of site (file)
            placed under site_url.
    """
    try:
        request = urllib2.Request(site_url)
        request.add_header("User-Agent", "My Python Crawler")
        opener = urllib2.build_opener()
        response = opener.open(request, timeout=5)
    except urllib2.HTTPError as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    except urllib2.URLError as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    except socket.timeout as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    except httplib.BadStatusLine as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    except UnicodeEncodeError as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    return response


def get_contents(site_url):
    """
        @returns string contents of site (file) placed under site_url.
    """
    response = open_url(site_url)

    if not response:
        return None

    try:
        contents = response.read()
    except LookupError as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    return contents


def get_html(site_url):
    """
        @returns string of site (file) placed under site_url
            (if it has HTML formatted data).
    """
    response = open_url(site_url)

    if not response:
        return None

    # Check if site_url contains HTML
    try:
        if not response.info()['content-type'].startswith('text/html'):
            return None
    except KeyError:
            return None

    encoding = response.headers.getparam('charset')
    if not encoding:
        encoding = 'utf-8'

    try:
        html = response.read().decode(encoding)
    except UnicodeDecodeError as error:
        html = response.read().decode('ascii')
        return html
    except LookupError as error:
        logger.info ( unicode (site_url) + " - " + unicode(error) )
        return None
    return html


def valid_url(url_string):
    """
        @returns True if url is valid http:// or https:// url, False if not.
    """
    match = re.match (HTTP_S_VALIDATION_REGEX, url_string)
    if not match:
        print "NOT VALID:", url_string
        return False
    else:
        return True


def has_html(url_string):
    """
        @return True if url_string is a valid url which leads to HTML page.
    """
    #TODO: Optimize
    if valid_url(url_string) and get_html(url_string):
        return True
    else:
        return False


def contains_xml(string):
    """
        @returns True if string contains XML formatted data.
    """
    parser = xml.parsers.expat.ParserCreate()
    try:
        parser.Parse(string)
        return True
    except Exception as error:
        logger.info ( unicode(error) )
        return False


def has_xml(url_string):
    """
        @returns True if url_string is a valid url which leads to XML page.
    """
    contents = get_contents(url_string)
    if valid_url(url_string) and contains_xml(contents):
        return True
    else:
        return False


def get_rss_properties(url_string):
    """
        @returns a dict with rss properties (used in graph database).
    """
    #TODO: Encoding
    contents = get_contents(url_string)
    doc = xml.dom.minidom.parseString(contents)
    result = {
        "title" : "None",
        "description" : "None",
        "language" : "None"
    }
    try:
        child_nodes = doc.childNodes
        if len(child_nodes) == 0:
            return result
        elements = child_nodes[0].getElementsByTagName("channel")
        if len(elements) == 0:
            return result
        channel = elements[0]

        for tag in ["title", "description", "language"]:
            elements = channel.getElementsByTagName(tag)
            if len(elements) == 0:
                return result
            child_nodes = elements[0].childNodes
            if len(child_nodes) == 0:
                return result
            result[tag] = child_nodes[0].nodeValue
    #TODO: Many XML formatting issues is a big problem
    # Instead of catching exceptions change XML parsing method
    except Exception as error:
        logger.info( unicode(error) )
    return result


def randpop(list_object):
    """
        @returns pops a random element
    """
    return list_object.pop(random.randint(0,len(list_object)-1))


