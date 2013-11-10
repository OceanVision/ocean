"""
Privileges represented as hierarchical structure
Every object is passed part of it

Note : prototyped only
"""
#TODO: implement fully

import copy



PRIVILEGE_WRITE = 1
PRIVILEGE_READ = 0

root = {"NewsWebsite": None, "News": None, "NeoUser": None}


root["NewsWebsite"] = {"label": PRIVILEGE_WRITE,
                       "description": PRIVILEGE_WRITE,
                       "image_width": PRIVILEGE_WRITE,
                       "image_height": PRIVILEGE_WRITE,
                       "image_link": PRIVILEGE_WRITE,
                       "image_url": PRIVILEGE_WRITE,
                       "language": PRIVILEGE_WRITE}

root["News"] = {"label": PRIVILEGE_WRITE,
                "link": PRIVILEGE_WRITE,
                "title": PRIVILEGE_WRITE,
                "description": PRIVILEGE_WRITE,
                "guid": PRIVILEGE_WRITE}



def construct_full_privilege():
    """ Get full privilege object """
    return copy.deepcopy(root)

def privileges_bigger_or_equal(privilege, needed_privilege):
    """ Try if is ok <=> All entries are bigger or equal """
    #TODO: implement
    return True