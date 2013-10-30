from django.db import models
from neo4django.db import models

# Create your models here.

class User (models.NodeModel):
    username = models.StringProperty()
    subscribes_to = models.Relationship ('self', rel_type='__subscribes_to__')

class NewsWebsite (models.NodeModel):
    url = models.URLProperty()

class News (models.NodeModel):
    url = models.URLProperty()
