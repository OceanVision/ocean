from django.contrib import admin
from models import UserProfile
from models import NeoUser, NewsWebsite, News

admin.site.register(UserProfile)
# TODO: doesnt work with neo4django ? no module neo4django.admin..
#admin.site.register(NeoUser)
#admin.site.register(NewsWebsite)
#admin.site.register(News)
