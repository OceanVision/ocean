import os
from django.db import models
from django.contrib.auth.models import User
from neo4django.db import models as neo4j_models
from py2neo import node
import sys
from graph_defines import *



def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    description = models.CharField(max_length=200)
    profile_image = models.ImageField(
        upload_to=get_image_path,
        blank=True,
        null=False
    )
    show_email = models.BooleanField()

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user.get_full_name()


class PrivateMessages(models.Model):
    sender = models.ForeignKey(User, related_name='sent')
    receiver = models.ForeignKey(User, related_name='received')
    message = models.CharField(max_length=2000)
    date = models.DateTimeField(auto_now_add=True) #When created set to "now"
    is_read = models.BooleanField()


class Contacts(models.Model):
    follower = models.ForeignKey(User, related_name='is_following')
    followed = models.ForeignKey(User, related_name='is_followed')


#TODO: remove after refactoring !!! - obsolete
class News(neo4j_models.NodeModel):
    #TODO: dodawac to dekoratorem, lub wlasny obiekt i dziedziczyc po nim
    def refresh(self):
        """ Reload an object from the database """
        return self.__class__._default_manager.get(pk=self.pk)

    uuid = neo4j_models.StringProperty()

    title = neo4j_models.StringProperty()

    link = neo4j_models.URLProperty()
    #First analytic field!
    loved_counter = neo4j_models.IntegerProperty(default=0)
    description = neo4j_models.StringProperty()
    guid = neo4j_models.URLProperty()
    pubdate = neo4j_models.StringProperty()


class Content(neo4j_models.NodeModel):
    #TODO: dodawac to dekoratorem, lub wlasny obiekt i dziedziczyc po nim
    def refresh(self):
        """ Reload an object from the database """
        return self.__class__._default_manager.get(pk=self.pk)

    uuid = neo4j_models.StringProperty()

    title = neo4j_models.StringProperty()

    link = neo4j_models.URLProperty()
    #First analytic field!
    loved_counter = neo4j_models.IntegerProperty(default=0)
    description = neo4j_models.StringProperty()
    guid = neo4j_models.URLProperty()
    pubdate = neo4j_models.StringProperty()


#TODO: remove after refactoring !!! - obsolete
class Website(neo4j_models.NodeModel):

    def refresh(self):
        """ Reload an object from the database """
        return self.__class__._default_manager.get(pk=self.pk)

    has = neo4j_models.Relationship('ContentSource', rel_type=HAS_RELATION, related_name='has')

    link = neo4j_models.URLProperty()
    title = neo4j_models.StringProperty()
    language = neo4j_models.StringProperty()


class ContentSource(neo4j_models.NodeModel):

    def refresh(self):
        """ Reload an object from the database """
        return self.__class__._default_manager.get(pk=self.pk)

    uuid = neo4j_models.StringProperty()

    #TODO: change to Content
    produces = neo4j_models.Relationship('News', rel_type=PRODUCES_RELATION, related_name="produced")

    link = neo4j_models.URLProperty()
    title = neo4j_models.StringProperty()
    description = neo4j_models.StringProperty()
    image_width = neo4j_models.IntegerProperty()
    image_height = neo4j_models.IntegerProperty()
    image_link = neo4j_models.URLProperty()
    image_url = neo4j_models.URLProperty()
    language = neo4j_models.StringProperty()
    source_type = neo4j_models.StringProperty()


class NeoUser(neo4j_models.NodeModel):
    """
        Auxiliary node in graph database, to query easy for subscribed websites
    """

    def refresh(self):
        """ Reload an object from the database """
        return self.__class__._default_manager.get(pk=self.pk)

    uuid = neo4j_models.StringProperty()

    subscribes_to = neo4j_models.Relationship(
        'ContentSource',
        rel_type=SUBSCRIBES_TO_RELATION,
        related_name="subscribed"
    )
    loves_it = neo4j_models.Relationship(
        "Content",
        rel_type=LOVES_IT_RELATION,
        related_name="loved"
    )

    # There has to be related user in django.contrib.auth.User !! TODO: relation?
    username = neo4j_models.StringProperty()


### DEPRECATED Models ###

#TODO: Delete following code after system refactorization

class NewsWebsite(neo4j_models.NodeModel):
    """
        DEPRECATED - will be deleted after refactorization
    """

    def refresh(self):
        """ Reload an object from the database """
        return self.__class__._default_manager.get(pk=self.pk)


    produces = neo4j_models.Relationship('News', rel_type=PRODUCES_RELATION, related_name="produced")

    link = neo4j_models.URLProperty()
    title = neo4j_models.StringProperty()
    description = neo4j_models.StringProperty()
    image_width = neo4j_models.IntegerProperty()
    image_height = neo4j_models.IntegerProperty()
    image_link = neo4j_models.URLProperty()
    image_url = neo4j_models.URLProperty()
    language = neo4j_models.StringProperty()
    source_type = neo4j_models.StringProperty()

#NOTE: End of future deletion

