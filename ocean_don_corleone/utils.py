import json
import urllib2, urllib


MASTER = "master"
def get_configuration(name):
    config = json.load(open("config.json","r"))
    params = urllib.urlencode({"name":name})
    response = json.loads(urllib2.urlopen(config[MASTER]+"/get_configuration?%s" % params).read())

    # Sometimes it is incompatible
    if isinstance(response, str) or isinstance(response, unicode):
        response = response.replace("http://127.0.0.1", "localhost")

    print name, response

    # Check if error
    if isinstance(response, str) or isinstance(response, unicode) and response[0:5] == "error": #ya, pretty lame;)
        raise response

    return response