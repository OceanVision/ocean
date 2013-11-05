from django.shortcuts import render
from models import NewsWebsite,News,NeoUser
from django.views.generic.detail import DetailView
from django.template import loader


def index(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        print request.user
        print NeoUser.objects.filter(username__exact="kudkudak")[0]._get_pk_val()

        print NeoUser.objects.filter(username__exact="kudkudak")[0].subscribes_to.all()
        u = NeoUser.objects.filter(username__exact="kudkudak")[0]
        print type(NeoUser.objects.filter(username__exact="kudkudak")[0])
        print u.subscribes_to.all()


        print u.subscribes_to.all().select_related('produces') #Add tests

        rss_items_array = []  # building news to be rendered (isn't very efficient..)

        n = 0
        for rss_website in u.subscribes_to.all():
            for news in rss_website.produces.all():
                n += 1
                rss_items_array += [{'category': 2, 'title': 'TestTitle '+str(n), 'description': news.url,
                                     'color': 'e5e5e5'}]
                #TODO: next iteration : add fetching

        #TODO: make color dependent of various features
        category_array = [{'name': 'Barack Obama', 'color': 'ffbd0c'},
                          {'name': 'tennis', 'color': '00c6c4'},
                          {'name': 'iPhone', 'color': '74899c'},
                          {'name': 'cooking', 'color': '976833'}]

        return render(request, 'rss/index.html', {'logged_in': True, 'rss_items': rss_items_array,
                                                  'categories': category_array})
    else:
        # Redirect anonymous users to login page.
        return render(request, 'rss/message.html', {'message': 'You are not logged in'})


#def index(request):
#    #from models import *
#
#    sub_list = NeoUser.objects.get_or_create(username=request.user)[0].subscribes_to.all()
#    sub_str = ''
#
#    for web in sub_list:
#        sub_str += web.url + '; '
#
#    if request.user.is_authenticated():
#        # Do something for authenticated users.
#        return render ( request, 'rss/message.html', {
#            'message': 'Hello, ' + str(request.user) + '! Here are your subscriptions: ' +
#            sub_str
#            }
#        )
#    else:
#        # Redirect anonymous users to login page.
#        return render(request, 'rss/message.html', {'message': 'You are not logged in'
#                                                        + str(request.user.objects.filter(username__exact="admin"))})
#
#    # TODO: add as unit test
#
#    n1 = NewsWebsite.objects.filter(url="http://antyweb.pl")
#    if len(n1) == 0:
#        n1 = NewsWebsite.objects.create(url="http://antyweb.pl")
#        print n1._get_pk_val()
#        n1.save()
#        print "Inserted ",n1
#
#    n2 = NewsWebsite.objects.filter(url="http://spidersweb.pl")
#    if len(n2) == 0:
#        n2 = NewsWebsite.objects.create(url="http://spidersweb.pl")
#        n2.save()
#        print n2._get_pk_val()
#        print "Inserted ",n2
#
#    u = NeoUser.objects.filter(username="admin")
#    print "Found ",u
#
#    if len(u) == 0:
#        u = NeoUser.objects.create(username="admin")
#        u.save()
#        print "Inserted ",u
#
#        u.subscribes_to.add(n1)
#        u.subscribes_to.add(n2)
#        print "subscribed to"
#        print u.subscribes_to.all() #Add tests
#        print u._get_pk_val()
#        print type(u)
#        u.save()
#        n1.save()
#        n2.save()
#
#    #str(NeoUser.objects.filter(username__exact="admin")[0].subscribes_to.all()[]