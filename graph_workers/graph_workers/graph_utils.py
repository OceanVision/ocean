""" Simple utility functions and objects """
import time
import os
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
import struct
import json
from dateutil import parser
import datetime

MY_DEBUG_LEVEL = 25
MY_INFO_LEVEL = 35
MY_INFO_IMPORTANT_LEVEL = 32
MY_IMPORTANT_LEVEL = 41
MY_CRITICAL_LEVEL = 51

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


def get_datetime_gmt_now():
    dt= datetime.datetime.utcnow()
    dt = dt.replace(tzinfo=timezone("GMT")) #TODO: should be UTC
    return dt

def database_timestamp_to_datetime(timestamp):
    """
        @param timestamp from database
        @returns datetime in GMT timezone
    """

    dt = datetime.datetime.fromtimestamp(timestamp)
    dt = dt.replace(tzinfo=timezone("GMT")) # Otherwise it would do a conversion -1h  (if given timezone as parameter)
    return dt


def datetime_to_database_timestamp(dt):
    """
        @param datetime in GMT timezone
        @returns timestamp in GMT timezone
    """
    #TODO: add checking for GMT timezone.
    return int(time.mktime(dt.timetuple()))


def database_gmt_now():
    return datetime_to_database_timestamp(get_datetime_gmt_now())


def database_gmt_minutes_expired(gmt_pair, minutes):
    """
        True if given minutes expired between gmt_pair[0] and gmt_pair[1].
    """
    return (gmt_pair[1] - gmt_pair[0]) > minutes*60


def get_domain(url_string):
    """
        @returns domain of given url_string
    """
    return urlparse.urlsplit(url_string)[1].split(':')[0]


def get_domain_url(url_string):
    """
        @returns domain of given url_string with scheme prefix
    """
    url_split = urlparse.urlsplit(url_string)
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
    url_pairs = re.findall(HTTP_S_LINK_REGEX, string)
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
        request = urllib2.Request(site_url.encode('ascii'))
        request.add_header("User-Agent", "My Python Crawler")
        opener = urllib2.build_opener()
        response = opener.open(request, timeout=5)
    except urllib2.HTTPError as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
        return None
    except urllib2.URLError as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
        return None
    except socket.timeout as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
        return None
    except httplib.BadStatusLine as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
        return None
    except UnicodeEncodeError as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
        return None
    except Exception as error:
        logger.info(unicode(site_url) + ' - ' + unicode(error))
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
    #except LookupError as error:
    except Exception as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
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
    except Exception as error:
        logger.info(unicode(site_url) + " - " + unicode(error))
        return None
    return html


def valid_url(url_string):
    """
        @returns True if url is valid http:// or https:// url, False if not.
    """
    match = re.match(HTTP_S_VALIDATION_REGEX, url_string)
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
        logger.info(unicode(error))
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
    result = {
        "title": "None",
        "description": "None",
        "language": "None"
    }
    #TODO: Encoding
    try:
        contents = get_contents(url_string)
        doc = xml.dom.minidom.parseString(contents)
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
        logger.info(unicode(error))
    return result


def randpop(list_object):
    """
        @returns pops a random element
    """
    return list_object.pop(random.randint(0, len(list_object) - 1))


import datetime, time, functools, operator, types

default_fudge = datetime.timedelta(seconds=0, microseconds=0, days=0)





def deep_eq(_v1, _v2, datetime_fudge=default_fudge, _assert=False):
    """
    Tests for deep equality between two python data structures recursing
    into sub-structures if necessary. Works with all python types including
    iterators and generators. This function was dreampt up to test API responses
    but could be used for anything. Be careful. With deeply nested structures
    you may blow the stack.

    Options:
              datetime_fudge => this is a datetime.timedelta object which, when
                                comparing dates, will accept values that differ
                                by the number of seconds specified
              _assert        => passing yes for this will raise an assertion error
                                when values do not match, instead of returning
                                false (very useful in combination with pdb)

    Doctests included:

    >>> x1, y1 = ({'a': 'b'}, {'a': 'b'})
    >>> deep_eq(x1, y1)
    True
    >>> x2, y2 = ({'a': 'b'}, {'b': 'a'})
    >>> deep_eq(x2, y2)
    False
    >>> x3, y3 = ({'a': {'b': 'c'}}, {'a': {'b': 'c'}})
    >>> deep_eq(x3, y3)
    True
    >>> x4, y4 = ({'c': 't', 'a': {'b': 'c'}}, {'a': {'b': 'n'}, 'c': 't'})
    >>> deep_eq(x4, y4)
    False
    >>> x5, y5 = ({'a': [1,2,3]}, {'a': [1,2,3]})
    >>> deep_eq(x5, y5)
    True
    >>> x6, y6 = ({'a': [1,'b',8]}, {'a': [2,'b',8]})
    >>> deep_eq(x6, y6)
    False
    >>> x7, y7 = ('a', 'a')
    >>> deep_eq(x7, y7)
    True
    >>> x8, y8 = (['p','n',['asdf']], ['p','n',['asdf']])
    >>> deep_eq(x8, y8)
    True
    >>> x9, y9 = (['p','n',['asdf',['omg']]], ['p', 'n', ['asdf',['nowai']]])
    >>> deep_eq(x9, y9)
    False
    >>> x10, y10 = (1, 2)
    >>> deep_eq(x10, y10)
    False
    >>> deep_eq((str(p) for p in xrange(10)), (str(p) for p in xrange(10)))
    True
    >>> str(deep_eq(range(4), range(4)))
    'True'
    >>> deep_eq(xrange(100), xrange(100))
    True
    >>> deep_eq(xrange(2), xrange(5))
    False
    >>> import datetime
    >>> from datetime import datetime as dt
    >>> d1, d2 = (dt.now(), dt.now() + datetime.timedelta(seconds=4))
    >>> deep_eq(d1, d2)
    False
    >>> deep_eq(d1, d2, datetime_fudge=datetime.timedelta(seconds=5))
    True
    """
    _deep_eq = functools.partial(deep_eq, datetime_fudge=datetime_fudge,
                                 _assert=_assert)

    def _check_assert(R, a, b, reason=''):
        if _assert and not R:
            assert 0, "an assertion has failed in deep_eq (%s) %s != %s" % (
                reason, str(a), str(b))
        return R

    def _deep_dict_eq(d1, d2):
        k1, k2 = (sorted(d1.keys()), sorted(d2.keys()))
        if k1 != k2: # keys should be exactly equal
            return _check_assert(False, k1, k2, "keys")

        return _check_assert(operator.eq(sum(_deep_eq(d1[k], d2[k])
                                             for k in k1),
                                         len(k1)), d1, d2, "dictionaries")

    def _deep_iter_eq(l1, l2):
        if len(l1) != len(l2):
            return _check_assert(False, l1, l2, "lengths")
        return _check_assert(operator.eq(sum(_deep_eq(v1, v2)
                                             for v1, v2 in zip(l1, l2)),
                                         len(l1)), l1, l2, "iterables")

    def op(a, b):
        _op = operator.eq
        if type(a) == datetime.datetime and type(b) == datetime.datetime:
            s = datetime_fudge.seconds
            t1, t2 = (time.mktime(a.timetuple()), time.mktime(b.timetuple()))
            l = t1 - t2
            l = -l if l > 0 else l
            return _check_assert((-s if s > 0 else s) <= l, a, b, "dates")
        return _check_assert(_op(a, b), a, b, "values")

    c1, c2 = (_v1, _v2)

    # guard against strings because they are iterable and their
    # elements yield iterables infinitely.
    # I N C E P T I O N
    for t in types.StringTypes:
        if isinstance(_v1, t):
            break
    else:
        if isinstance(_v1, types.DictType):
            op = _deep_dict_eq
        else:
            try:
                c1, c2 = (list(iter(_v1)), list(iter(_v2)))
            except TypeError:
                c1, c2 = _v1, _v2
            else:
                op = _deep_iter_eq

    return op(c1, c2)



class deep_eq_wrapper(object):
    """ Wrapper for keeping deep_eq objects """
    def __init__(self, v):
        self.v = v
    def __eq__(self, other):
        return deep_eq(self.v, other.v)
    def __hash__(self):
        return str(self.v).__hash__()
    def __str__(self):
        return str(self.v)


""" Utils for prefix length TCP """
def socket_read_n(sock, n):
    """ Read exactly n bytes from the socket.
        Raise RuntimeError if the connection closed before
        n bytes were read.
    """
    buf = ''
    while n > 0:
        data = sock.recv(n)
        if data == '':
            raise RuntimeError('unexpected connection close')
        buf += data
        n -= len(data)
    return buf


def get_message_raw(sock):
    """
        Returns raw message (using length prefix framing)
    """
    len_buf = socket_read_n(sock, 4) # Read exactly n bytes
    msg_len = struct.unpack('>L', len_buf)[0]
    msg_buf = socket_read_n(sock,msg_len)
    return msg_buf


def send_message_raw(sock, msg ):
    """
        Sends raw message (using length prefix framing)
    """
    print "Sending "+msg
    packed_len = struct.pack('>L', len(msg)) # Number of bytes
    sock.sendall(packed_len + msg)


def send_message(sock, msg):
    """
        Sends message of class message_class (using length prefix framing)
    """
    s = json.dumps(msg)
    packed_len = struct.pack('>L', len(s)) # Number of bytes
    sock.sendall(packed_len + s)


def get_message(sock):
    """
        Returns object deserialized by JSON (using length prefix framing)
    """
    len_buf = socket_read_n(sock, 4) # Read exactly n bytes
    msg_len = struct.unpack('>L', len_buf)[0]
    msg_buf = socket_read_n(sock,msg_len)
    return json.loads(msg_buf)


def error_handle_odm(func):
    """
    This decorator will return response to message.html with error if caught
    """
    def f(request, *args, **dict_args):
        try:
            return func(request, *args, **dict_args)
        except Exception, e:
            print '{0} failed: {1}.'.format(func.__name__, e)
            return {}
        except:
            print '{0} failed with not registered error.'.format(func.__name__)
            return {}

    f.__name__ = func.__name__
    return f
