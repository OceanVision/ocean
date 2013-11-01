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


class NeoUser (neo4j_models.NodeModel):
    username = neo4j_models.StringProperty()
    subscribes_to = neo4j_models.Relationship('self', rel_type='__subscribes_to__')


class NewsWebsite (neo4j_models.NodeModel):
    url = neo4j_models.URLProperty()


class News (neo4j_models.NodeModel):
    url = neo4j_models.URLProperty()
