import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('~/.virtualenvs/ocean/local/lib/python2.7/site-packages')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../webservice")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../graph_views")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../graph_workers")))



os.environ['DJANGO_SETTINGS_MODULE'] = 'ocean.settings'

# Activate your virtual env
# TODO: change this line
# TODO: change this line to stop being node_specific
activate_env=os.path.expanduser("/home/staszek/.virtualenvs/ocean/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))



import ocean_graph_view_manager
#TODO: rewrite OM as a service
ocean_graph_view_manager.OC = ocean_graph_view_manager.OceanGraphViewManager()
ocean_graph_view_manager.OC.run()
print ocean_graph_view_manager.OC


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

