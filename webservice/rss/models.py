import os
from django.db import models
from django.contrib.auth.models import User
from neo4django.db import models

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    description = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return User.get_full_name()


class NeoUser (models.NodeModel):
    username = models.StringProperty()
    subscribes_to = models.Relationship ('self', rel_type='__subscribes_to__')


class NewsWebsite (models.NodeModel):
    url = models.URLProperty()


class News (models.NodeModel):
    url = models.URLProperty()
