import os
from django.db import models
from django.contrib.auth.models import User
from neo4django.db import models as neo4j_models

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    description = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return User.get_full_name()





class News (neo4j_models.NodeModel):
    label = neo4j_models.StringProperty(default="__news__")
    slug = neo4j_models.StringProperty() # slug-field is used to create nice-urls
    url = neo4j_models.URLProperty()



class NewsWebsite (neo4j_models.NodeModel):
    label = neo4j_models.StringProperty(default="__news_website__")

    produces = neo4j_models.Relationship('News', rel_type='__produces__', related_name="produced")

    url = neo4j_models.URLProperty()


class NeoUser (neo4j_models.NodeModel):
    """
        Auxiliary node in graph database, to query easy for subscribed websites
    """
    label = neo4j_models.StringProperty(default="__user__")
    # There has to be related user in django.contrib.auth.User !! TODO: relation?
    username = neo4j_models.StringProperty()

    subscribes_to = neo4j_models.Relationship('NewsWebsite', rel_type='__subscribes_to__', related_name="subscribed")


