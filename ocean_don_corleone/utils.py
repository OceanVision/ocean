import json
import urllib2, urllib


MASTER = "master"
def get_configuration(name):
    config = json.load(open("config.json","r"))
    params = urllib.urlencode({"name":name})
    response = urllib2.urlopen(config[MASTER]+"/get_configuration?%s" % params).read()

    if response[0:5] == "error": #ya, pretty lame;)
        raise response

    return response